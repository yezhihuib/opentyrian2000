int main(int argc,char**argv){
 CHECK(argc==2);snprintf(work,sizeof work,"%s",argv[1]);snprintf(full,sizeof full,"%s/full",work);snprintf(path,sizeof path,"%s/bank.bin",work);FILE*f=fopen(path,"rb");CHECK(f);banksize=fread(originalbank,1,sizeof originalbank,f);fclose(f);snprintf(path,sizeof path,"%s/records.bin",work);f=fopen(path,"rb");CHECK(f&&fread(recordbytes,1,sizeof recordbytes,f)==sizeof recordbytes);fclose(f);
 for(unsigned role=0;role<10;role++){
  const ShadowRole*r=roles+role;if(r->mode_index!=1)continue;
  for(unsigned p=2;p<=3;p++)for(int d=4;d<=8;d+=4){
   unsigned k=r->member[p],raw=ids[k];CHECK(raw==294||raw==295);prepare(r,p,0,d);
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
 rear_p1_shutdown();printf("Actual current P7 cold/warm/cache/header/density/birth gate checks PASS: %u\n",checks);return 0;
}
