# Amplicon-Illumina




#Step_1
./Amplicon_PairedEnd_GATK4_Annovar_hg38.sh




#Step_2
python3 IlluminaAmpiconGATKAnnovarDemux.py -Library Amplicon_Library_Details.xlsx -Coverage Target_Region_CveredWith_Atleast20X.csv -Folder Annovar -EndofFile hg38_multiannoDesiredColumns.tsv                        

          ##Target_Region_CveredWith_Atleast20X.csv is present in the mosedepth folder, name may be 20X.csv 




#Sep_3

python3 Amplicon_sequencing_demultiplex_Variant_SampleSummary.py 


