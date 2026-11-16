#include "scale_rule.h"
#include <iostream>
#include <limits>
void fails(auto f){bool ok=false;try{f();}catch(const std::exception&){ok=true;}mousa::require(ok,"expected rejection");}
int main(){
 int checked=0;
 for(int tonic=60;tonic<72;++tonic)for(auto offsets:{std::vector<int>{0,2,4,5,7,9,11},std::vector<int>{0,4,5,7,11}}){
  mousa::ScaleRule rule(tonic,12,offsets);
  for(int current=48;current<=84;++current)if(rule.contains(current)){
   auto allowed=rule.allowed(current);std::vector<double> logits(49,1e6);for(int k:allowed)logits[k]=-1e6;
   auto p=mousa::masked_distribution(logits,allowed);double total=0;
   for(int k=0;k<49;++k){bool valid=std::find(allowed.begin(),allowed.end(),k)!=allowed.end();mousa::require(valid?p[k]>0:p[k]==0,"forbidden mass or underflow");if(p[k]>0)mousa::require(rule.contains(current+k-24),"off-scale output");total+=p[k];}
   mousa::require(std::abs(total-1)<1e-12,"normalization");++checked;
  }
 }
 fails([]{mousa::ScaleRule(60,12,{0,0,4});});fails([]{mousa::ScaleRule(60,12,{2,4});});
 fails([]{mousa::ScaleRule(60,12,{0,4}).allowed(61);});fails([]{mousa::masked_distribution(std::vector<double>(49,0),{});});
 fails([]{mousa::masked_distribution(std::vector<double>(49,0),{24,24});});
 fails([]{mousa::masked_distribution(std::vector<double>(49,std::numeric_limits<double>::quiet_NaN()),{24});});
 std::cout<<checked<<" scale/key/current-note supports and six rejection cases passed\\n";
}
