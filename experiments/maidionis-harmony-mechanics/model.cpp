#include "maidionis/model.h"
#include <torch/torch.h>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <iostream>
#include <random>
#include <ctime>
#include <fcntl.h>
#include <unistd.h>

using namespace maidionis;
namespace fs = std::filesystem;
constexpr int width=192, stride=64;
const char* task="mousa.harmony-degree-mechanics.experimental.v1";
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
std::string read(const fs::path& p){
 std::ifstream f(p,std::ios::binary);require(bool(f),"cannot read input");std::ostringstream s;s<<f.rdbuf();
 require(s.str().size()<=32*1024*1024,"file bound");return s.str();
}
void write(const fs::path& p,const std::string& s){
 int fd=::open(p.c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);require(fd>=0,"output exists/unavailable");
 size_t pos=0;while(pos<s.size()){auto n=::write(fd,s.data()+pos,s.size()-pos);if(n<0&&errno==EINTR)continue;require(n>0,"write failed");pos+=size_t(n);}
 require(::fsync(fd)==0&&::close(fd)==0,"flush failed");
}
int integer(const Json& v,int low,int high){
 require(v.is_number_integer()&&v.get<double>()>=low&&v.get<double>()<=high,"integer/range required");return v.get<int>();
}
void label_ok(int label,int count){require(label>=0&&label<width&&label%stride<count,"invalid degree label");}
ModelConfig config(){ModelConfig c;c.kind="encoder";c.hidden_width=256;c.input_width=2;
 c.output_width=width;c.vocabulary=278;c.controls={1};c.dropout_milli=0;return c;}
Batch batch(const Json& rows){
 require(rows.is_array()&&!rows.empty()&&rows.size()<=64,"batch bound");std::vector<int64_t>x,y;
 for(auto&r:rows){
  require(r.is_object()&&r.size()==8,"row schema");
  require(r.at("family_id").is_string()&&!r.at("family_id").get<std::string>().empty()&&r.at("family_id").get<std::string>().size()<=256,"family identity");
  int count=integer(r.at("degree_count"),7,7);require(r.at("history").is_array()&&r.at("history").size()==8,"history bound");
  x.push_back(1);x.push_back(194+count);
  for(auto&v:r.at("history")){int value=integer(v,0,width-1);label_ok(value,count);x.push_back(value+2);}
  x.push_back(259+integer(r.at("chord_root"),0,6));
  x.push_back(266+integer(r.at("chord_seventh"),0,1));
  x.push_back(268+integer(r.at("phase"),0,7));
  x.push_back(276+integer(r.at("gap_index"),0,1));
  int target=integer(r.at("target"),0,width-1);label_ok(target,count);y.push_back(target);
 }

 Batch b;b.inputs=torch::from_blob(x.data(),{int64_t(rows.size()),14},torch::kInt64).clone();
 b.targets=torch::from_blob(y.data(),{int64_t(rows.size())},torch::kInt64).clone();b.mask=b.inputs.ne(0);
 b.segments=torch::zeros_like(b.inputs);b.target_mask=torch::ones_like(b.targets,torch::kBool);return b;
}
torch::Tensor logits(ModelPtr m,const Batch& b){
 auto z=m->forward(b);auto count=b.inputs.select(1,1)-194;
 auto invalid=torch::arange(width,b.inputs.options()).remainder(stride).unsqueeze(0)>=count.unsqueeze(1);
 return z.masked_fill(invalid,-1e9);
}
double training_nll(ModelPtr m,const Json& rows){
 m->eval();torch::NoGradGuard guard;double total=0;size_t count=0;
 for(size_t start=0;start<rows.size();start+=64){Json part=Json::array();for(size_t i=start;i<std::min(start+64,rows.size());++i)part.push_back(rows[i]);
  auto b=batch(part);total+=categorical_loss(logits(m,b),b.targets,b.target_mask).item<double>()*part.size();count+=part.size();}
 return total/count;
}
int main(int argc,char**argv){try{
 require(argc==3||argc==4,"train DATA OUTDIR | validate DATA | serve MODEL");std::string mode=argv[1];auto started=std::clock();
 auto budget=[&]{require(double(std::clock()-started)/CLOCKS_PER_SEC<90,"CPU budget exceeded");};
 auto c=config();
 if(mode=="train"||mode=="validate"){
  require(argc==(mode=="train"?4:3),"train DATA OUTDIR | validate DATA");auto raw=read(argv[2]);auto d=parse_json(raw,2*1024*1024);
  require(d.is_object()&&d.size()==3&&d.at("schema")=="mousa.harmony-degree-training.experimental.v1"&&d.at("task_id")==task,"training task mismatch");
  const auto& rows=d.at("rows");require(rows.is_array()&&rows.size()>=1&&rows.size()<=4096,"dataset bound");
  // Validate every row before construction, not only sampled rows.
  for(auto&r:rows)batch(Json::array({r}));
  if(mode=="validate"){std::cout<<"validated "<<rows.size()<<" rows; no model construction or fitting\n";return 0;}
  fs::path out=argv[3];require(!fs::exists(out),"output exists");if(!out.parent_path().empty())fs::create_directories(out.parent_path());require(fs::create_directory(out),"output create failed");
  auto m=make_seeded_model(c,314);torch::optim::AdamW optimizer(m->parameters(),torch::optim::AdamWOptions(0.0003).weight_decay(0));
  auto before=m->parameters()[0].detach().clone();double initial=training_nll(m,rows);std::mt19937 rng(314);Json losses=Json::array();
  for(int step=0;step<60;++step){budget();Json selected=Json::array();for(int i=0;i<32;++i)selected.push_back(rows[rng()%rows.size()]);
   auto b=batch(selected);m->train();optimizer.zero_grad();auto loss=categorical_loss(logits(m,b),b.targets,b.target_mask);
   require(torch::isfinite(loss).item<bool>(),"nonfinite loss");loss.backward();
   for(auto&p:m->parameters())require(p.grad().defined()&&torch::isfinite(p.grad()).all().item<bool>(),"invalid gradient");
   torch::nn::utils::clip_grad_norm_(m->parameters(),1);optimizer.step();m->enforce_constraints();losses.push_back(loss.item<double>());
  }
  double delta=(m->parameters()[0]-before).abs().sum().item<double>();require(delta>0,"no parameter update");double final=training_nll(m,rows);
  auto weights=save_model_bytes(m);write(out/"weights.pt",weights);
  // Keep optimizer state for research provenance; this driver does not claim resume qualification.
  torch::serialize::OutputArchive oa;optimizer.save(oa);std::ostringstream os;oa.save_to(os);write(out/"optimizer.pt",os.str());
  auto reloaded=make_seeded_model(c,999);load_model_bytes(reloaded,weights);auto probe=batch(Json::array({rows[0]}));
  m->eval();reloaded->eval();torch::NoGradGuard guard;require(torch::equal(logits(m,probe),logits(reloaded,probe)),"reload changed logits");
  Json manifest={{"schema","mousa.harmony-degree-model.experimental.v1"},{"task_id",task},{"model_config",c.json()},
   {"weights_sha256",sha256(weights)},{"optimizer_sha256",sha256(os.str())},{"data_sha256",sha256(raw)},
   {"steps",60},{"seed",314},{"training_rows",rows.size()},{"initial_training_nll",initial},{"final_training_nll",final},
   {"embedding_delta_l1",delta},{"losses",losses},{"reload_logits_exact",true},{"environment",parse_json(numerical_environment())},
   {"cpu_seconds",double(std::clock()-started)/CLOCKS_PER_SEC},{"usage","original train-only harmony-conditioning mechanics fixture; no held-out or music-quality claim"}};
  write(out/"manifest.json",manifest.dump(2)+"\n");std::cout<<"harmony degree mechanics trained and saved\n";
 }else if(mode=="serve"){
  require(argc==3,"serve MODEL");fs::path dir=argv[2];
  auto mf=parse_json(read(dir/"manifest.json"));
  require(mf.at("schema")=="mousa.harmony-degree-model.experimental.v1"&&mf.at("task_id")==task&&mf.at("model_config")==c.json(),"incompatible harmony model; legacy degree/semitone weights cannot be relabeled");
  auto weights=read(dir/"weights.pt");require(sha256(weights)==mf.at("weights_sha256").get<std::string>(),"weights digest mismatch");
  auto m=make_seeded_model(c,314);load_model_bytes(m,weights);m->eval();torch::NoGradGuard guard;
  std::string line;for(int query=0;std::getline(std::cin,line);++query){
   budget();require(query<2400&&line.size()<=1024*1024,"query bound");
   auto rows=parse_json(line);auto b=batch(rows);auto p=torch::softmax(logits(m,b).to(torch::kFloat64),1);Json result=Json::array();
   for(size_t i=0;i<rows.size();++i){Json probabilities=Json::array();for(int k=0;k<width;++k){double value=p[i][k].item<double>();require(std::isfinite(value),"nonfinite probabilities");if(k%stride>=7)require(value==0,"forbidden degree probability");probabilities.push_back(value);}result.push_back({{"probabilities",probabilities}});}
   std::cout<<result.dump()<<std::endl;
  }
 }else require(false,"unsupported mode");
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
