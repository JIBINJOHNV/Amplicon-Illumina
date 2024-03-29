



import pandas as pd
import glob
import argparse
import os
pd.options.display.float_format = "{:,.2f}".format
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)



parser=argparse.ArgumentParser(description="This script split the multiplex amplicon annovar file to sample wise")
parser.add_argument('-Library','--Library', help="Library details; should have  [#chrom	Start	End	f_NAME	Library	Amp-1; Amp-1 means barcodeid the file should be xlsx", required=True)

parser.add_argument('-Coverage','--Coverage', help=" File should have folowing columns ; and tab separated; #chrom', 'start', 'end', 'f_NAME', 'TotalRegion', 'Amp-1:>=20X'", required=True)

parser.add_argument('-Folder','--Folder', help="folder path where Annovar file present; should end with / ; Annovar Fils should be like ;Amp-1.hg38_multiannoDesiredColumns.tsv", required=True)
parser.add_argument('-EndofFile','--EndofFile', help="End of annovar file; for identifying the annovar file ; eg: hg38_multiannoDesiredColumns.tsv", required=True)


args=parser.parse_args()
Library=args.Library
Coverage=args.Coverage
Folder=args.Folder
EndofFile="*"+args.EndofFile



#Library="Amplicon_Library_Details1.xlsx"
#Coverage="20X.csv"
#Folder="Annovar/"
#EndofFile="*"+"hg38_multiannoDesiredColumns.tsv"




os.system("mkdir -p SampleWise_Annovar")     
os.system("mkdir -p SampleWise_Annovar/Present")
os.system("mkdir -p SampleWise_Annovar/NotPresent")


#Sample details
S_Details=pd.read_excel(Library,sheet_name="Sample_Details")
S_Details.iloc[:,5:]=S_Details.iloc[:,5:].apply(lambda x: x.astype(str).str.upper())
S_Details['Sample ID']=S_Details['Sample ID'].str.strip()
S_Details['Sample ID']=S_Details['Sample ID'].str.upper()
S_Details['Sample Name'] = S_Details['Sample Name'].str.replace(' ', '')
S_Details['Sample Name'] =S_Details['Sample Name'].str.lstrip()
S_Details['Disease']=S_Details['Disease'].str.lstrip().str.replace(' ', '_')




#Sample details
#Sample details
M_fILE=pd.read_excel(Library,sheet_name="Amplicon_Library_Distribution")
M_fILE[['Region_Start','Region_End']]=M_fILE[['Region_Start','Region_End']].astype(int)

for column in M_fILE.iloc[:,5:].columns:
    #print(M_fILE[column])
    M_fILE[column]=M_fILE[column].str.replace(' ', '')
    M_fILE[column] = M_fILE[column].str.lstrip()

#Coverage
Depth20X=pd.read_csv(Coverage,sep="\t")
files = glob.glob(Folder+EndofFile)

#print(Depth20X.columns,M_fILE.columns)






def greetings(sample_id):
        global PrioritisedDf, NoPrioritisedVariants_df
        #Identify the sample specific region and MERGING WITH SAMPLE DETAILS
        Library_withSample=[]  #IDENTIFYING SAMPLE IN WHICH LIBRARY
        SampleSpecificRegiondf=pd.DataFrame(columns=list(M_fILE.iloc[:,:5])) 
        
        for library in M_fILE.columns[5:]:
                selectdf=M_fILE[M_fILE[library].isin([sample_id])]
                if selectdf.empty:
                    pass   
                else:
                    SampleSpecificRegiondf=SampleSpecificRegiondf.append(selectdf.iloc[:,0:4])
                    SampleSpecificRegiondf['Library']=library
                    SampleSpecificRegiondf['Sample ID']=sample_id
                    Library_withSample.append(library)
        SampleSpecificRegion_SampleInfo_df=pd.merge(SampleSpecificRegiondf,S_Details,on='Sample ID')
        #Incorporate 20X depth information to SampleSpecificRegion_SampleInfo_df
        Selected_DF_Depth=pd.DataFrame()
        DepthDfColumns=['Depth_#chrom', 'Depth_start', 'Depth_end', 'f_NAME', 'TotalRegion']
        
        for sample in Library_withSample:
                listToStr = ' '.join(Depth20X.columns) 
                if sample+':>=20X' in listToStr:
                    DepthDfColumns.append(sample+':>=20X')
        
        for i in range(SampleSpecificRegion_SampleInfo_df.shape[0]):
                chr=SampleSpecificRegion_SampleInfo_df.iloc[i,0]
                start=SampleSpecificRegion_SampleInfo_df.iloc[i,1]
                end=SampleSpecificRegion_SampleInfo_df.iloc[i,2]
               
                Selected_DF_Depth_temp=Depth20X[(Depth20X['Depth_#chrom']==chr) & (Depth20X['Depth_start']>=float(start)) &
                                          (Depth20X['Depth_end']<=float(end))][DepthDfColumns]
                Selected_DF_Depth=Selected_DF_Depth.append(Selected_DF_Depth_temp)
        #print(Selected_DF_Depth)
        
        Selected_DF_Depth=Selected_DF_Depth.drop(['f_NAME'],axis=1).rename(columns={'Library':'Library_mix'})
        SampleSpecificRegion_SampleInfo_df[['Region_Start','Region_End']]=SampleSpecificRegion_SampleInfo_df[['Region_Start','Region_End']].apply(pd.to_numeric, axis = 1)
        Selected_DF_Depth[['Depth_start','Depth_end']]=Selected_DF_Depth[['Depth_start','Depth_end']].apply(pd.to_numeric, axis = 1)
        
        #print(SampleSpecificRegion_SampleInfo_df.columns,Selected_DF_Depth.columns)
        
        SampleSpecificRegion_SampleInfo_Depth_df=pd.merge(SampleSpecificRegion_SampleInfo_df,Selected_DF_Depth,
                                                    left_on=['Region_#chrom', 'Region_Start', 'Region_End'],
                               right_on=['Depth_#chrom', 'Depth_start', 'Depth_end'],how='outer').rename(columns={'Fragments':'No_of_Fragments'})
        
        Annovardf=pd.DataFrame()
        for library in Library_withSample:
                for Annovarfile in [x for x in files if library+"." in x]:
                        Annovardf=pd.read_csv(Annovarfile,sep="\t")
                        try:
                                Annovardf=Annovardf.drop([x for x in Annovardf.columns if 'Unnamed:' in x],axis=1)
                        except:
                                Annovardf=Annovardf.append(Annovardf) 
        
        #Extract the smple specifc variants/gene from the above annovar file
        Columns=list(Annovardf.columns)+list(SampleSpecificRegion_SampleInfo_Depth_df.columns)
        Selected_DF=pd.DataFrame(columns=Columns)
        for i in range(SampleSpecificRegion_SampleInfo_Depth_df.shape[0]):
                chr=SampleSpecificRegion_SampleInfo_Depth_df.iloc[i,0]
                start=SampleSpecificRegion_SampleInfo_Depth_df.iloc[i,1]
                end=SampleSpecificRegion_SampleInfo_Depth_df.iloc[i,2]
                                
                Selected_AnnovarDf=Annovardf[(Annovardf['#Chr']==chr) & (Annovardf['Start']>=start) & \
                                     (Annovardf['End']<=end)]
                #If the above annovar df not contain df
                Selected_AnnovarEmptyDf=pd.DataFrame()
                if not Selected_AnnovarDf.empty:
                    for (key,value) in dict(SampleSpecificRegion_SampleInfo_Depth_df.iloc[i,:]).items():
                        Selected_AnnovarDf[key]=value
                    #print(Selected_AnnovarDf.head())
                    Selected_AnnovarDf=Selected_AnnovarDf.reindex(Selected_DF.columns, axis=1)
                    Selected_DF=Selected_DF.append(Selected_AnnovarDf)
                                
                else:
                    #Incorporating THE PARTICULAR AMPLICON SEQUENCED IN WHICH LIBRARIES
                    M_fILE_temp=M_fILE[(M_fILE['Region_#chrom']==chr) & (M_fILE['Region_Start']>=start) & \
                                     (M_fILE['Region_End']<=end)]
                    
                    for (key,value) in dict(M_fILE_temp).items():
                        
                        if key.split()[0]=="Library":
                            SampleSpecificRegion_SampleInfo_Depth_df.iloc[i,9]=str(value).split()[1]
                
                    #iNCORPORATING AMPLICON SIZE
                    Selected_D_temp=Depth20X[(Depth20X['Depth_#chrom']==chr) & (Depth20X['Depth_start']>=start) & (Depth20X['Depth_end']<=end)]
                    for (key,value) in dict(Selected_D_temp).items():
                        
                        if key.split()[0]=='TotalRegion':
                                SampleSpecificRegion_SampleInfo_Depth_df.iloc[i,10]=str(value).split()[1]
                    Selected_DF=Selected_DF.append(SampleSpecificRegion_SampleInfo_Depth_df.iloc[i,:])
        
        #Save file
        NameDf=S_Details[S_Details['Sample ID']==sample_id]
        sid=NameDf['Sample ID']
        sname="-".join(NameDf['Sample Name'].to_string().split()[1:])
        try:
                sname=sname.replace("/",'')
        except:
                sname=sname
        sGene=NameDf['Gene'].to_string().split()[1]
        sFragments=NameDf['Fragments'].to_string().split()[1]
        sDisease=NameDf['Disease'].to_string().split()[1]
        FileName=sid+"_"+sname+"_"+sDisease+"_"+sGene+"_"+str(sFragments)+"_"+'_'.join(Library_withSample)
        
        FiltDf=Selected_DF.copy()
        FiltDf=FiltDf[FiltDf["Func.refGene"].isin(['exonic','splicing','exonic;splicing'])]
        NonCodVariation=['synonymous SNV','unknown'] #,'nonframeshift insertion', 'nonframeshift deletion'
        FiltDf=FiltDf[~FiltDf['ExonicFunc.refGene'].isin(NonCodVariation)]
        FiltDf=FiltDf[FiltDf['MAX_MAF']<0.01]
        
        if not FiltDf.empty:
                Selected_DF.to_csv("SampleWise_Annovar/"+FileName.to_string().split()[1]+"_multiannoDesiredColumns.csv",index=None)
                FiltDf['NofFragments']=Selected_DF['No_of_Fragments'].astype(int).max()
                FiltDf['Sequenced_Fragemnts_Name']=','.join(Selected_DF['f_NAME'].unique())
                FiltDf['Sequenced_Fragemnts_Name_count']=len(Selected_DF['f_NAME'].unique())
                try:
                    LT_95=Selected_DF[Selected_DF['_'.join(Library_withSample)+':>=20X'].astype(int)<95]
                    FiltDf['Amplicon_with_lt<95%_20Xcoverage']=str(dict(zip(LT_95.f_NAME, LT_95['_'.join(Library_withSample)+':>=20X'])))
                except:
                    FiltDf['Amplicon_with_lt<95%_20Xcoverage']=0
                
                try:
                        MT_95=Selected_DF[Selected_DF['_'.join(Library_withSample)+':>=20X'].astype(int)>=95]
                        FiltDf['Amplicon_with_Mt>=95%_20Xcoverage']=str(dict(zip(MT_95.f_NAME, MT_95['_'.join(Library_withSample)+':>=20X'])))
                except:
                        FiltDf['Amplicon_with_lt>=95%_20Xcoverage']=0
                FiltDf["Sequenced_Library"]='_'.join(Library_withSample)
                FiltDf=FiltDf.drop('_'.join(Library_withSample)+':>=20X',axis=1)
                FiltDf.rename(columns={'_'.join(Library_withSample):"Genotype_With_Qscore"},inplace=True)
                FiltDf.to_csv("SampleWise_Annovar/Present/"+FileName.to_string().split()[1]+"_multiannoDesiredColumns_Filtered_Present.csv",index=None)
        if  FiltDf.empty:
                Selected_DF.to_csv("SampleWise_Annovar/"+FileName.to_string().split()[1]+"_multiannoDesiredColumns.csv",index=None)
                NameDf2=S_Details[S_Details['Sample ID']==sample_id]
                NameDf2['NofFragments']=Selected_DF['No_of_Fragments'].astype(int).max()
                NameDf2['Sequenced_Fragemnts_Name']=','.join(Selected_DF['f_NAME'].unique())
                NameDf2['Sequenced_Fragemnts_Name_count']=len(Selected_DF['f_NAME'].unique())
                try:
                        LT_95=Selected_DF[Selected_DF['_'.join(Library_withSample)+':>=20X'].astype(int)<95]
                        NameDf2['Amplicon_with_lt<95%_20Xcoverage']=str(dict(zip(LT_95.f_NAME, LT_95['_'.join(Library_withSample)+':>=20X'])))
                except:
                        NameDf2['Amplicon_with_lt<95%_20Xcoverage']=0
                try:
                        MT_95=Selected_DF[Selected_DF['_'.join(Library_withSample)+':>=20X'].astype(int)>=95]
                        NameDf2['Amplicon_with_Mt>=95%_20Xcoverage']=str(dict(zip(MT_95.f_NAME, MT_95['_'.join(Library_withSample)+':>=20X'])))
                except:
                        NameDf2['Amplicon_with_lt>=95%_20Xcoverage']=0
                NameDf2["Sequenced_Library"]='_'.join(Library_withSample)
                NameDf2.to_csv("SampleWise_Annovar/NotPresent/"+FileName.to_string().split()[1]+"_multiannoDesiredColumns_Filtered_NotPresent.csv",index=None)
                
 


for sampleid in S_Details['Sample ID']:
    try:
        greetings(sampleid)
        print("Started for the sample " +sampleid)
    except:
        print("\n\nNot able to processes " +sampleid,'\n\n')
