#include "maidionis/model.h"
#include <torch/torch.h>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <iostream>
#include <random>
#include <set>
#include <ctime>
#include <fcntl.h>
#include <unistd.h>
#include <cerrno>
using namespace maidionis;
namespace fs=std::filesystem;
#ifndef MOUSA_PROGRESSION_CONTEXT
#define MOUSA_PROGRESSION_CONTEXT 8
#endif
constexpr int CONTEXT=MOUSA_PROGRESSION_CONTEXT;
static_assert(CONTEXT==2||CONTEXT==8,"only registered context profiles");
const char* TASK=CONTEXT==2?"mousa.major-progression-local2.weak-label.experimental.v1":"mousa.major-progression.weak-label.experimental.v1";
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
std::string read(const fs::path& p){
 std::ifstream f(p,std::ios::binary|std::ios::ate);require(bool(f),"cannot read input");
 require(f.tellg()>=0&&f.tellg()<=32*1024*1024,"file bound");f.seekg(0);std::ostringstream s;s<<f.rdbuf();return s.str();
}
void write(const fs::path& p,const std::string& s){
 int fd=::open(p.c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);require(fd>=0,"exclusive output failed");
 size_t pos=0;while(pos<s.size()){auto n=::write(fd,s.data()+pos,s.size()-pos);if(n<0&&errno==EINTR)continue;require(n>0,"write failed");pos+=size_t(n);}
 require(::fsync(fd)==0,"fsync failed");require(::close(fd)==0,"close failed");
}
int integer(const Json& v,int low,int high){require(v.is_number_integer()&&v.get<double>()>=low&&v.get<double>()<=high,"integer/range required");return v.get<int>();}
ModelConfig config(){ModelConfig c;c.kind="encoder";c.hidden_width=256;c.input_width=2;c.output_width=14;c.vocabulary=16;c.controls={1};c.dropout_milli=0;return c;}
void rowcheck(const Json& r){
 require(r.is_object()&&r.size()==4&&r.contains("family")&&r.contains("input")&&r.contains("label")&&r.contains("index"),"row schema");
 require(r.at("family").is_string()&&!r.at("family").get<std::string>().empty()&&r.at("family").get<std::string>().size()<=256,"family identity");
 integer(r.at("index"),CONTEXT,10000000);integer(r.at("label"),0,13);
 const auto& x=r.at("input");require(x.is_array()&&x.size()==CONTEXT+1,"input length");require(integer(x[0],1,1)==1,"task token");
 for(size_t i=1;i<CONTEXT+1;++i)integer(x[i],2,15);
}
void data_check(const Json& d){
 require(d.is_object()&&d.size()==4&&d.at("schema")=="mousa.progression-training.experimental.v1"&&d.at("task_id")==TASK,"data identity");
 std::set<std::string> trainfamilies;
 for(auto key:{"train","test"}){
  const auto& rows=d.at(key);require(rows.is_array()&&!rows.empty()&&rows.size()<=(std::string(key)=="train"?16384:4096),"dataset bound");
  std::set<std::string> identities;
  for(const auto& r:rows){rowcheck(r);auto family=r.at("family").get<std::string>();
   require(identities.insert(family+":"+r.at("index").dump()).second,"duplicate identity");
   if(std::string(key)=="train")trainfamilies.insert(family);else require(!trainfamilies.contains(family),"family leakage");
  }
 }
}
Batch batch(const Json& rows){
 require(rows.is_array()&&!rows.empty()&&rows.size()<=64,"batch bound");std::vector<int64_t>x,y;
 for(const auto&r:rows){rowcheck(r);for(auto&v:r.at("input"))x.push_back(v.get<int64_t>());y.push_back(r.at("label").get<int64_t>());}
 Batch b;b.inputs=torch::from_blob(x.data(),{int64_t(rows.size()),CONTEXT+1},torch::kInt64).clone();b.targets=torch::from_blob(y.data(),{int64_t(rows.size())},torch::kInt64).clone();
 b.mask=b.inputs.ne(0);b.segments=torch::zeros_like(b.inputs);b.target_mask=torch::ones_like(b.targets,torch::kBool);return b;
}
Json subset(const Json& rows,size_t start,size_t size=32){Json result=Json::array();for(size_t i=start;i<std::min(start+size,rows.size());++i)result.push_back(rows[i]);return result;}
Json evaluate(ModelPtr m,const Json& rows,bool with_probabilities=false){
 m->eval();torch::NoGradGuard guard;Json result=Json::array();
 for(size_t start=0;start<rows.size();start+=32){auto part=subset(rows,start);auto b=batch(part);auto z=m->forward(b);auto lp=torch::log_softmax(z,1);auto probs=torch::softmax(z.to(torch::kFloat64),1);auto pred=z.argmax(1);
  for(size_t i=0;i<part.size();++i){int target=part[i].at("label"),prediction=pred[i].item<int>();Json row={{"family",part[i].at("family")},{"index",part[i].at("index")},{"target",target},{"prediction",prediction},{"correct",target==prediction},{"nll",-lp[i][target].item<double>()}};
   if(with_probabilities){row["probabilities"]=Json::array();for(int k=0;k<14;++k)row["probabilities"].push_back(probs[i][k].item<double>());}result.push_back(row);
  }
 }
 return result;
}
Json aggregate(const Json& rows){double loss=0,correct=0;for(const auto&r:rows){loss+=r.at("nll").get<double>();correct+=r.at("correct").get<bool>()?1:0;}return {{"rows",rows.size()},{"mean_nll",loss/rows.size()},{"accuracy",correct/rows.size()}};}
ModelPtr load(const fs::path& dir){
 auto mf=Json::parse(read(dir/"manifest.json"));require(mf.at("schema")=="mousa.progression-model.experimental.v1"&&mf.at("task_id")==TASK&&mf.at("complete")==true&&mf.at("context_length").is_number_integer()&&mf.at("context_length")==CONTEXT&&mf.at("model_config")==config().json(),"model identity");
 auto weights=read(dir/"weights.pt");require(sha256(weights)==mf.at("weights_sha256").get<std::string>(),"weights digest");auto m=make_seeded_model(config(),314);load_model_bytes(m,weights);return m;
}
int main(int argc,char**argv){try{
 require(argc==3||argc==4,"train DATA OUT | validate DATA | serve MODEL");std::string mode=argv[1];auto started=std::clock();auto budget=[&]{require(double(std::clock()-started)/CLOCKS_PER_SEC<90,"CPU budget exceeded");};
 if(mode=="train"||mode=="validate"){
  require(argc==(mode=="train"?4:3),"train DATA OUT | validate DATA");auto raw=read(argv[2]);auto d=Json::parse(raw);data_check(d);
  if(mode=="validate"){std::cout<<"validated "<<d.at("train").size()<<" train and "<<d.at("test").size()<<" test rows; no model construction or fitting\n";return 0;}
  fs::path out=argv[3];require(!fs::exists(out),"output exists");auto m=make_seeded_model(config(),314);torch::optim::AdamW optimizer(m->parameters(),torch::optim::AdamWOptions(.0003).weight_decay(0));
  auto before=m->parameters()[0].detach().clone();Json result={{"initial_test",evaluate(m,d.at("test"))},{"losses",Json::array()}};std::mt19937 rng(314);std::string schedule;Json sampled_indices=Json::array();
  for(int step=0;step<60;++step){budget();Json selected=Json::array();for(int i=0;i<32;++i){auto index=rng()%d.at("train").size();selected.push_back(d.at("train")[index]);schedule+=std::to_string(index)+",";sampled_indices.push_back(index);}
   auto b=batch(selected);m->train();optimizer.zero_grad();auto loss=categorical_loss(m->forward(b),b.targets,b.target_mask);require(torch::isfinite(loss).item<bool>(),"nonfinite loss");loss.backward();
   for(auto&p:m->parameters())require(p.grad().defined()&&torch::isfinite(p.grad()).all().item<bool>(),"invalid gradient");torch::nn::utils::clip_grad_norm_(m->parameters(),1);optimizer.step();m->enforce_constraints();result["losses"].push_back(loss.item<double>());
  }
  budget();result["final_test"]=evaluate(m,d.at("test"));result["initial_aggregate"]=aggregate(result["initial_test"]);result["final_aggregate"]=aggregate(result["final_test"]);
  result["embedding_delta_l1"]=(m->parameters()[0]-before).abs().sum().item<double>();require(result["embedding_delta_l1"].get<double>()>0,"no parameter update");result["schedule_indices_sha256"]=sha256(schedule);result["sampled_indices"]=sampled_indices;
  auto weights=save_model_bytes(m);auto reloaded=make_seeded_model(config(),999);load_model_bytes(reloaded,weights);m->eval();reloaded->eval();{torch::NoGradGuard guard;auto probe=batch(subset(d.at("train"),0));require(torch::equal(m->forward(probe),reloaded->forward(probe)),"reload logits mismatch");}
  result["reload_logits_exact"]=true;torch::serialize::OutputArchive oa;optimizer.save(oa);std::ostringstream os;oa.save_to(os);budget();result["cpu_seconds"]=double(std::clock()-started)/CLOCKS_PER_SEC;
  if(!out.parent_path().empty())fs::create_directories(out.parent_path());require(fs::create_directory(out),"output race");write(out/"weights.pt",weights);write(out/"optimizer.pt",os.str());write(out/"results.json",result.dump(2)+"\n");
  Json mf={{"schema","mousa.progression-model.experimental.v1"},{"task_id",TASK},{"context_length",CONTEXT},{"complete",true},{"model_config",config().json()},{"weights_sha256",sha256(weights)},{"optimizer_sha256",sha256(os.str())},{"results_sha256",sha256(read(out/"results.json"))},{"data_sha256",sha256(raw)},{"steps",60},{"batch_size",32},{"seed",314},{"train_rows",d.at("train").size()},{"test_rows",d.at("test").size()},{"environment",parse_json(numerical_environment())},{"usage","weak-label chord-progression research; automatic analysis is not human harmonic truth or musical quality"}};
  write(out/"manifest.json",mf.dump(2)+"\n");std::cout<<"trained 60 fixed steps\n";
 }else if(mode=="serve"){
  require(argc==3,"serve MODEL");auto m=load(argv[2]);std::string line;
  for(int query=0;std::getline(std::cin,line);++query){budget();require(query<2400&&line.size()<=1024*1024,"query bound");auto rows=Json::parse(line);require(rows.is_array()&&!rows.empty()&&rows.size()<=64,"batch bound");for(auto&r:rows)rowcheck(r);std::cout<<evaluate(m,rows,true).dump()<<std::endl;}
 }else require(false,"unsupported mode");return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
