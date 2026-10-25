int main(int argc,char**argv){
 unsigned lobes203cases=0,lobes43cases=0,rear281cases=0,rear1cases=0,rear39cases=0,p7cases=0;
 CHECK(argc==2);snprintf(work,sizeof work,"%s",argv[1]);snprintf(full,sizeof full,"%s/full",work);snprintf(path,sizeof path,"%s/bank.bin",work);FILE*f=fopen(path,"rb");CHECK(f);banksize=fread(originalbank,1,sizeof originalbank,f);fclose(f);snprintf(path,sizeof path,"%s/records.bin",work);f=fopen(path,"rb");CHECK(f&&fread(recordbytes,1,sizeof recordbytes,f)==sizeof recordbytes);fclose(f);
 for(unsigned role=0;role<sizeof roles/sizeof *roles;role++){
  const ShadowRole*r=roles+role;
  for(unsigned p=0;p<r->count;p++)for(int d=4;d<=8;d+=4){
   unsigned k=r->member[p],raw=ids[k];if(raw!=203&&raw!=222&&raw!=43&&raw!=5&&raw!=281&&raw!=282&&raw!=300&&raw!=301&&raw!=277&&raw!=278&&raw!=296&&raw!=297&&raw!=298&&raw!=299&&raw!=1&&raw!=2&&raw!=3&&raw!=77&&raw!=39&&raw!=40&&raw!=41&&raw!=294&&raw!=295)continue;
#ifdef WRONG_LOBES203
   if(raw!=203&&raw!=222)continue;
#endif
#ifdef WRONG_LOBES43
   if(raw!=43&&raw!=5)continue;
#endif
#ifdef WRONG_REAR281
   if(raw!=281&&raw!=282&&raw!=300&&raw!=301&&raw!=277&&raw!=278&&raw!=296&&raw!=297&&raw!=298&&raw!=299)continue;
#endif
#ifdef WRONG_REAR1
   if(raw!=1&&raw!=2&&raw!=3&&raw!=77)continue;
#endif
#ifdef WRONG_REAR39
   if(raw!=39&&raw!=40&&raw!=41)continue;
#endif
#ifdef WRONG_P7
   if(raw!=294&&raw!=295)continue;
#endif
   if(raw==203||raw==222)lobes203cases++;else if(raw==43||raw==5)lobes43cases++;else if(raw==281||raw==282||raw==300||raw==301||raw==277||raw==278||raw==296||raw==297||raw==298||raw==299)rear281cases++;else if(raw==1||raw==2||raw==3||raw==77)rear1cases++;else if(raw==39||raw==40||raw==41)rear39cases++;else p7cases++;
   prepare(r,p,0,d);
#ifdef EXPECT_WRONG_PINS
   CHECK(!checked_head(k,0));CHECK(!shadow(r,p,0));continue;
#else
   unsigned opens=role_opens;CHECK(checked_head(k,0));CHECK(role_opens==opens+1);CHECK(checked_head(k,0));CHECK(role_opens==opens+1);
   Asset*a=rear_p1_asset(raw);CHECK(a&&a->bank==131&&a->index==(int)raw);char file[4096];int z=snprintf(file,sizeof file,"%s/rear-multicannon-p1-bank8-%u-%d.hda",full,raw,d);CHECK(z>0&&(size_t)z<sizeof file);f=fopen(file,"rb");CHECK(f&&fseek(f,28,SEEK_SET)==0);for(unsigned i=0;i<168u*d*d*4u;i++)CHECK(fgetc(f)==a->rgba[i]);CHECK(fgetc(f)==EOF);fclose(f);
   /* warm backing file change does not change retained cache; cold load rejects */
   f=fopen(file,"r+b");CHECK(f&&fseek(f,28,SEEK_SET)==0);int original=fgetc(f);CHECK(original>=0&&fseek(f,28,SEEK_SET)==0&&fputc(original^1,f)!=EOF);fclose(f);CHECK(checked_head(k,0));prepare(r,p,0,d);CHECK(!checked_head(k,0));
   f=fopen(file,"r+b");CHECK(f&&fseek(f,28,SEEK_SET)==0&&fputc(original,f)!=EOF);fclose(f);CHECK(!checked_head(k,0));prepare(r,p,0,d);CHECK(checked_head(k,0));
   /* supported Hard normal versus rejected Hard shadow; birth must be emitted in scope */
   defaults(d,full);lvlFileNum=15;initialDifficulty=DIFFICULTY_HARD;test_power=r->power;emit(k,0);CHECK(checked_head(k,0));CHECK(!shadow(r,p,0));
   prepare(r,p,0,d);CHECK(shadow(r,p,0)==(d==8));if(d==8){CHECK(vulcan_shadow.shadow_rgba==rear_p1_asset(raw)->rgba);VulcanShadowCall v=vulcan_shadow;rear_p1_reset(&rear_p1_state);CHECK(!rear_p11_shadow_birth(&v));}
#endif
  }
 }

#ifdef WRONG_LOBES203
 CHECK(lobes203cases==4&&lobes43cases==0&&rear281cases==0&&rear1cases==0&&rear39cases==0&&p7cases==0);
#elif defined(WRONG_LOBES43)
 CHECK(lobes203cases==0&&lobes43cases==4&&rear281cases==0&&rear1cases==0&&rear39cases==0&&p7cases==0);
#elif defined(WRONG_REAR281)
 CHECK(rear281cases==112&&rear1cases==0&&rear39cases==0&&p7cases==0);
#elif defined(WRONG_REAR1)
 CHECK(rear281cases==0&&rear1cases==34&&rear39cases==0&&p7cases==0);
#elif defined(WRONG_REAR39)
 CHECK(rear281cases==0&&rear1cases==0&&rear39cases==20&&p7cases==0);
#elif defined(WRONG_P7)
 CHECK(rear281cases==0&&rear1cases==0&&rear39cases==0&&p7cases==20);
#else
 CHECK(lobes203cases==4&&lobes43cases==4&&rear281cases==112&&rear1cases==34&&rear39cases==20&&p7cases==20);
#endif
 rear_p1_shutdown();printf("Actual current Rear lobes + Rear281 + Rear1 + Rear39 + P7 cold/warm/cache/header/density/birth gate checks PASS: %u\n",checks);return 0;
}
