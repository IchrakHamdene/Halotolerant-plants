# Halotolerant-plants
## To Create a Functional Metagenome Prediction and Add Descriptions Using PICRUSt2
picrust2_pipeline.py --i dna_sequences.fasta --s feature_table.biom --o picrust2 --p 1

add_descriptions.py --i path_abun_unstrat.tsv --m METACYC --o path_abun_unstrat_desc.tsv

add_descriptions.py --i pred_metagenome_unstrat.tsv --m EC --o pred_metagenome_unstrat_desc.tsv

add_descriptions.py --i pred_metagenome_unstrat.tsv --m KO --o pred_metagenome_unstrat_desc.tsv

### Import data (manifest file should be formatted by the user)

qiime tools import --type 'SampleData[PairedEndSequencesWithQuality]' --input-path manifest.txt --output-path paired-end-demux.qza --input-format PairedEndFastqManifestPhred33V2

### Screening of raw data

qiime demux summarize --i-data paired-end-demuz.qza --o-visualization raw_data.qzv
	
### Denoising and OTU picking using DADA2 

qiime dada2 denoise-paired --p-trunc-len-f 280 --p-trunc-len-r 280 --i-demultiplexed-seqs paired-end-demux.qza --p-n-threads 36 --o-table OTU_table.qza --o-representative-sequences rep_seqs.qza  --o-denoising-stats dada2_stats.qza

### Table summary

qiime feature-table summarize --i-table OTU_table.qza --m-sample-metadata-file  Metadata.txt --o-visualization OTU_table_after_DADA2.qzv

###According to the summary, the best rarefaction value is 6000.

#### Taxonomic Annotation

qiime feature-classifier classify-sklearn --i-classifier classifier.qza --i-reads rep_seqs.qza --p-n-jobs 24 --o-classification taxonomy.qza 

### Removing reads classified as Chloroplasts and Mitochondria

qiime taxa filter-table --i-table OTU_table.qza --i-taxonomy taxonomy.qza --p-exclude chloroplast,mitochondria --o-filtered-table OTU_table_noclp_nomit.qza

### Table summary

qiime feature-table summarize --i-table OTU_table_noclp_nomit.qza --m-sample-metadata-file  Metadata.txt --o-visualization OTU_table_noclp_nomit.qzv

### Taxonomy barcharts

qiime taxa barplot --i-table OTU_table_noclp_nomit.qza --i-taxonomy taxonomy.qza --m-metadata-file Metadata.txt --o-visualization taxa-bar-plots.qzv
	
### Phylogenetic tree reconstruction on the OTUs

qiime phylogeny align-to-tree-mafft-fasttree --i-sequences rep_seqs.qza --o-alignment aligned_rep_seqs.qza --o-masked-alignment masked_aligned_rep_seqs.qza --o-tree unrooted_tree.qza --o-rooted-tree rooted_tree.qza

### Diversity parameters calculation at a rarefaction of 6000

qiime diversity core-metrics-phylogenetic --i-phylogeny rooted_tree.qza --i-table OTU_table_noclp_nomit.qza --p-sampling-depth 6000 --m-metadata-file Metadata.txt --output-dir core-metrics-results

### Significance of single diversity parameters values among categorical variables - Shannon
qiime diversity alpha-group-significance --i-alpha-diversity core-metrics-results/shannon_vector.qza --m-metadata-file Metadata.txt --o-visualization core-metrics-results/shannon-group-significance.qzv

#### Rarefaction plots

qiime diversity alpha-rarefaction \
	--i-table OTU_table_noclp_nomit.qza	\
	--i-phylogeny rooted_tree.qza \
	--p-max-depth 1000 \
	--m-metadata-file Metadata.txt \
	--o-visualization core-metrics-results/rarefaction_analysis.qzv
	
### Collapsing the table at the genus level 

qiime taxa collapse \
	--i-table OTU_table_noclp_nomit.qza \
	--i-taxonomy taxonomy.qza \
	--p-level 6 \
	--o-collapsed-table OTU_table_genus.qza

### Exporting the table at the genus level 

qiime tools export \
	--input-path OTU_table_genus.qza \
	--output-path exported_tables

