// Saved-model inference adapted from Mousa PR #18 (ce10fd62); historical evidence is unchanged.
#include "maidionis/model.h"
#include "scale_rule.h"
#include <set>
#include <torch/torch.h>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <iostream>
#include <random>
#include <cmath>
#include <ctime>
#include <fcntl.h>
#include <unistd.h>
#include <cerrno>
using namespace maidionis;
namespace fs=std::filesystem;
void check(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
std::string read(const fs::path& path){std::ifstream f(path,std::ios::binary);check(bool(f),"cannot read input");std::ostringstream s;s<<f.rdbuf();return s.str();}
void write_exclusive(const fs::path& path,const std::string& bytes){int fd=::open(path.c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);check(fd>=0,"exclusive output create failed");size_t pos=0;while(pos<bytes.size()){auto n=::write(fd,bytes.data()+pos,bytes.size()-pos);if(n<0&&errno==EINTR)continue;if(n<=0){::close(fd);throw std::runtime_error("output write failed");}pos+=size_t(n);}if(::fsync(fd)!=0){::close(fd);throw std::runtime_error("output sync failed");}check(::close(fd)==0,"output close failed");}
Batch batch(const std::vector<int64_t>& pitch,const std::vector<int64_t>& rhythm){check(pitch.size()==8&&rhythm.size()==8,"history length");std::vector<int64_t> tokens;for(int64_t task:{1,2}){tokens.push_back(task);for(size_t i=0;i<8;++i){check(pitch[i]>=0&&pitch[i]<49&&rhythm[i]>=0&&rhythm[i]<25,"history token");tokens.push_back(pitch[i]+3);tokens.push_back(rhythm[i]+52);}}Batch b;b.inputs=torch::from_blob(tokens.data(),{2,17},torch::kInt64).clone();b.mask=b.inputs.ne(0);b.segments=torch::zeros_like(b.inputs);return b;}
std::vector<double> values(torch::Tensor logits){
 check(torch::isfinite(logits).all().item<bool>(),"nonfinite logits");
 std::vector<double> out;for(int i=0;i<49;++i)out.push_back(logits[i].item<double>());return out;
}
struct Draw{int label;uint32_t word;std::vector<double> probabilities;};
Draw draw(const std::vector<double>& logits,const std::vector<int>& allowed,std::mt19937& rng){
 auto p=mousa::masked_distribution(logits,allowed);uint32_t word=rng();
 double u=double(word)/4294967296.0,total=0;int picked=allowed.back();
 for(auto k:allowed){total+=p[k];if(u<total){picked=k;break;}}return {picked,word,p};
}
void fields(const Json& value,std::initializer_list<const char*> expected){
 check(value.is_object(),"object required");std::set<std::string> names;
 for(auto name:expected)names.insert(name);check(value.size()==names.size(),"unknown/missing fields");
 for(auto&item:value.items())check(names.contains(item.key()),"unknown field");
}
int semitones(const Json& value){
 check(value.is_number(),"numeric cents required");double x=value.get<double>();
 check(std::isfinite(x)&&x>=0&&x<=4800&&std::fmod(x,100)==0,"unsupported microtonal scale for semitone-only checkpoint");return int(x/100);
}
mousa::ScaleRule scale_rule(const Json& r){
 fields(r,{"schema","condition","scale","seeds"});
 check(r.at("schema")=="mousa.scale-generation-request.experimental.v1","request version");
 check(r.at("seeds")==Json::array({101,102,103}),"fixed seed protocol");
 const auto& c=r.at("condition");const auto& s=r.at("scale");
 fields(c,{"schema_version","scale_id","scale_sha256","key"});
 fields(s,{"scale_id","name","intervals_cents","period_cents","traditions","genre_tags","approximation","source_urls"});
 check(c.at("schema_version")=="mousa.scale-condition.experimental.v1","condition version");
 check(c.at("scale_id")==s.at("scale_id")&&c.at("scale_sha256")==sha256(s.dump(-1,' ',true)),"scale identity/digest mismatch");
 const auto& k=c.at("key");fields(k,{"tonic_midi","tonic_offset_cents","reference_a4_hz"});
 check(k.at("tonic_midi").is_number_integer()&&k.at("tonic_midi").get<double>()>=48&&k.at("tonic_midi").get<double>()<=84,"integer tonic in48..84 required");
 check(k.at("tonic_offset_cents").is_number()&&k.at("tonic_offset_cents").get<double>()==0&&
       k.at("reference_a4_hz").is_number()&&k.at("reference_a4_hz").get<double>()==440,"unsupported saved-model tuning");
 check(s.at("intervals_cents").is_array()&&s.at("intervals_cents").size()<=64,"scale interval bound");
 std::vector<int> offsets;for(auto&v:s.at("intervals_cents"))offsets.push_back(semitones(v));
 return {k.at("tonic_midi").get<int>(),semitones(s.at("period_cents")),offsets};
}
int main(int argc,char**argv){try{
 check(argc==4,"CHECKPOINT_DIR SCALE_REQUEST_JSON OUTPUT_JSON required");fs::path dir=argv[1],out=argv[3];auto request=parse_json(read(argv[2]));auto rule=scale_rule(request);check(!fs::exists(out),"output exists");auto started=std::clock();auto guard=[&](){check(double(std::clock()-started)/CLOCKS_PER_SEC<=60,"CPU budget exceeded");};
 auto manifest_bytes=read(dir/"manifest.json");check(sha256(manifest_bytes)=="123c378362a73c4e2ff54da539fa47b4ebabbd29afc2767d540b751cc36bd4db","manifest pin mismatch");auto manifest=Json::parse(manifest_bytes);check(manifest.at("complete")==true&&manifest.at("completed_epochs")==2&&manifest.at("total_steps")==512,"checkpoint incomplete/wrong version");check(manifest.at("data_sha256")=="2dbc239ad8c735d6a38473dc3d7f58e295e07d6e01acc650e3fd1473646f2f5d","checkpoint data pin");
 auto weights=read(dir/"weights.pt");check(sha256(weights)==manifest.at("weights_sha256").get<std::string>()&&sha256(weights)=="34dd1e168367a12390d2b10c1bf534459c24413a8460e74555da63b625d5d7f7","weights pin mismatch");ModelConfig c;c.kind="encoder";c.hidden_width=256;c.input_width=2;c.output_width=49;c.vocabulary=77;c.controls={1,2};c.dropout_milli=0;check(manifest.at("model_config")==c.json(),"model config mismatch");auto m=make_seeded_model(c,42);load_model_bytes(m,weights);m->eval();torch::NoGradGuard no_grad;
 Json result={{"request",request},{"schema","mousa.scale-generation-result.experimental.v1"},{"weights_sha256",sha256(weights)},{"manifest_sha256",sha256(manifest_bytes)},{"environment",parse_json(numerical_environment())},{"trained",false},{"ppq",480},{"end_tick",15360},{"tempo_bpm",100},{"meter",{4,4}},{"rng","std::mt19937(seed); one uint32/2^32 cumulative draw per task, pitch then rhythm, ascending allowed class order; final un-emitted next pitch also drawn"},{"samples",Json::array()}};
 for(int seed:{101,102,103}){std::mt19937 rng(seed);std::vector<int64_t> ph={24,26,26,23,24,22,26,24},rh={10,10,12,10,10,12,10,10};int tick=0,pitch=rule.tonic;Json events=Json::array(),trace=Json::array();while(tick<15360){guard();check(events.size()<128,"event count bound");auto b=batch(ph,rh);auto logits=m->forward(b);auto pp=values(logits[0]),rp=values(logits[1]);auto pa=rule.allowed(pitch);std::vector<int> ra;for(int k:{8,10,12,14}){int gap=120*(1<<((k-8)/2));if(tick+gap<=15360)ra.push_back(k);}auto pd=draw(pp,pa,rng),rd=draw(rp,ra,rng);int gap=120*(1<<((rd.label-8)/2));int duration=gap*9/10;events.push_back({{"onset_tick",tick},{"pitch",pitch},{"duration_ticks",duration},{"velocity",80},{"channel",0}});trace.push_back({{"onset_tick",tick},{"history_pitch",ph},{"history_rhythm",rh},{"pitch_label",pd.label},{"rhythm_label",rd.label},{"gap_ticks",gap},{"pitch_rng_word",pd.word},{"rhythm_rng_word",rd.word},{"raw_pitch_logits",pp},{"raw_rhythm_logits",rp},{"allowed_pitch_labels",pa},{"constrained_pitch_probabilities",pd.probabilities},{"constrained_rhythm_probabilities",rd.probabilities}});ph.erase(ph.begin());ph.push_back(pd.label);rh.erase(rh.begin());rh.push_back(rd.label);tick+=gap;pitch+=pd.label-24;}
 check(tick==15360,"wrong duration");result["samples"].push_back({{"seed",seed},{"events",events},{"trace",trace},{"event_count",events.size()},{"synthetic_primer_emitted",false}});
 }
 guard();result["cpu_seconds"]=double(std::clock()-started)/CLOCKS_PER_SEC;write_exclusive(out,result.dump(2)+"\n");std::cout<<"three seeds generated; cpu="<<result["cpu_seconds"]<<"\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
