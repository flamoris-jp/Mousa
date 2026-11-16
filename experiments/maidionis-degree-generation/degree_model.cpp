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
const char* task="mousa.absolute-degree.experimental.v1";
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
 c.output_width=width;c.vocabulary=259;c.controls={1};c.dropout_milli=0;return c;}
Batch batch(const Json& rows){
 require(rows.is_array()&&!rows.empty()&&rows.size()<=64,"batch bound");std::vector<int64_t>x,y;
 for(auto&r:rows){int count=integer(r.at("degree_count"),1,64);require(r.at("history").is_array()&&r.at("history").size()==8,"history bound");
  x.push_back(1);x.push_back(194+count);
  for(auto&v:r.at("history")){int value=integer(v,0,width-1);label_ok(value,count);x.push_back(value+2);}
  int target=integer(r.at("target"),0,width-1);label_ok(target,count);y.push_back(target);
 }
 Batch b;b.inputs=torch::from_blob(x.data(),{int64_t(rows.size()),10},torch::kInt64).clone();
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
 require(argc==4||argc==5,"train DATA OUTDIR or generate MODEL REQUEST OUTPUT");std::string mode=argv[1];auto started=std::clock();
 auto budget=[&]{require(double(std::clock()-started)/CLOCKS_PER_SEC<90,"CPU budget exceeded");};
 auto c=config();
 if(mode=="train"){
  require(argc==4,"train DATA OUTDIR");auto raw=read(argv[2]);auto d=parse_json(raw,2*1024*1024);
  require(d.at("schema")=="mousa.degree-training-data.experimental.v1"&&d.at("task_id")==task,"training task mismatch");
  const auto& rows=d.at("rows");require(rows.is_array()&&rows.size()>=1&&rows.size()<=4096,"dataset bound");
  // Validate every row before construction, not only sampled rows.
  for(auto&r:rows)batch(Json::array({r}));
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
  Json manifest={{"schema","mousa.degree-model.experimental.v1"},{"task_id",task},{"model_config",c.json()},
   {"weights_sha256",sha256(weights)},{"optimizer_sha256",sha256(os.str())},{"data_sha256",sha256(raw)},
   {"steps",60},{"seed",314},{"training_rows",rows.size()},{"initial_training_nll",initial},{"final_training_nll",final},
   {"embedding_delta_l1",delta},{"losses",losses},{"reload_logits_exact",true},{"environment",parse_json(numerical_environment())},
   {"cpu_seconds",double(std::clock()-started)/CLOCKS_PER_SEC},{"usage","train-only mechanical fixture; no music-quality/generalization claim"}};
  write(out/"manifest.json",manifest.dump(2)+"\n");std::cout<<"degree model trained and saved\n";
 }else if(mode=="generate"){
  require(argc==5,"generate MODEL REQUEST OUTPUT");fs::path dir=argv[2],out=argv[4];require(!fs::exists(out),"output exists");
  auto manifest_raw=read(dir/"manifest.json");auto mf=parse_json(manifest_raw);
  require(mf.at("schema")=="mousa.degree-model.experimental.v1"&&mf.at("task_id")==task&&mf.at("model_config")==c.json(),"incompatible degree model; legacy semitone weights cannot be relabeled");
  auto weights=read(dir/"weights.pt");require(sha256(weights)==mf.at("weights_sha256").get<std::string>(),"weights digest mismatch");
  auto q=parse_json(read(argv[3]));require(q.is_object()&&q.size()==5&&q.at("schema")=="mousa.degree-request.experimental.v1"&&q.at("task_id")==task,"degree request schema");
  int count=integer(q.at("degree_count"),1,64),seed=integer(q.at("seed"),0,2147483647),length=integer(q.at("length"),1,128);
  auto m=make_seeded_model(c,314);load_model_bytes(m,weights);m->eval();torch::NoGradGuard guard;
  std::vector<int> history(8,64);Json trace=Json::array(),labels=Json::array();std::mt19937 rng(seed);
  for(int i=0;i<length;++i){budget();Json row={{"degree_count",count},{"history",history},{"target",64}};
   auto z=logits(m,batch(Json::array({row})))[0].to(torch::kFloat64);auto p=torch::softmax(z,0);
   uint32_t word=rng();double u=double(word)/4294967296.0,total=0;int selected=-1;Json probabilities=Json::array();
   for(int k=0;k<width;++k){double value=p[k].item<double>();require(std::isfinite(value),"nonfinite probabilities");
    if(k%64>=count)require(value==0,"invalid degree probability");probabilities.push_back(value);
    if(k%64<count){total+=value;if(selected<0&&u<total)selected=k;}}
   require(selected>=0,"categorical sampling failed");label_ok(selected,count);
   Json raw=Json::array();for(int k=0;k<width;++k)raw.push_back(z[k].item<double>());
   trace.push_back({{"history",history},{"label",selected},{"rng_word",word},{"probabilities",probabilities},{"logits",raw}});labels.push_back(selected);
   history.erase(history.begin());history.push_back(selected);
  }
  Json result={{"schema","mousa.degree-result.experimental.v1"},{"task_id",task},{"request",q},
   {"manifest_sha256",sha256(manifest_raw)},{"weights_sha256",sha256(weights)},{"labels",labels},{"trace",trace},
   {"cpu_seconds",double(std::clock()-started)/CLOCKS_PER_SEC}};
  write(out,result.dump(2)+"\n");std::cout<<"degree sequence generated\n";
 }else require(false,"unsupported mode");
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
