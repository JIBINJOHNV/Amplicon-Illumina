# Amplicon-Illumina




# Step_1
./Amplicon_PairedEnd_GATK4_Annovar_hg38.sh




# Step_2

python3 Scripts/2_IlluminaAmpiconGATKAnnovarDemux.py \
                    -Library TestData/Amplicon_Library_Details1.xlsx \
                    -Coverage TestData/20X.csv \
                    -Folder TestData/Annovar/  \
                    -EndofFile hg38_multiannoDesiredColumns.tsv 


          ##Column names of  Amplicon_Library_Details1.xlsx and 20X.csv files should not change




# Sep_3

python3 Scripts/3_Amplicon_sequencing_demultiplex_Variant_SampleSummary.py


  
