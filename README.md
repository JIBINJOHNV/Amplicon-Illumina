# Amplicon-Illumina




#Step_1
./Amplicon_PairedEnd_GATK4_Annovar_hg38.sh




#Step_2
python3 2_IlluminaAmpiconGATKAnnovarDemux.py -Library Amplicon_Library_Details.xlsx -Coverage 20X.csv -Folder Annovar -EndofFile hg38_multiannoDesiredColumns.tsv 

#Sep_3

python3 3_Amplicon_sequencing_demultiplex_Variant_SampleSummary.py 


