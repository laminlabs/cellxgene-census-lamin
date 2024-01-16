import pandas as pd


def register_genes():
    import lamindb as ln
    import lnschema_bionty as lb

    organisms = lb.Organism.lookup(field=lb.Organism.scientific_name)
    genes_files = {
        "homo_sapiens": "https://github.com/chanzuckerberg/single-cell-curation/raw/main/cellxgene_schema_cli/cellxgene_schema/ontology_files/genes_homo_sapiens.csv.gz",
        "mus_musculus": "https://github.com/chanzuckerberg/single-cell-curation/raw/main/cellxgene_schema_cli/cellxgene_schema/ontology_files/genes_mus_musculus.csv.gz",
        "synthetic_construct": "https://github.com/chanzuckerberg/single-cell-curation/raw/main/cellxgene_schema_cli/cellxgene_schema/ontology_files/genes_ercc.csv.gz",
        "severe_acute_respiratory_syndrome_coronavirus_2": "https://github.com/chanzuckerberg/single-cell-curation/raw/main/cellxgene_schema_cli/cellxgene_schema/ontology_files/genes_sars_cov_2.csv.gz",
    }

    # register all genes for each organism
    for organism_name, genes_file in genes_files.items():
        print(f"registering {organism_name} genes")
        df = pd.read_csv(genes_file, header=None, index_col=0)
        organism_record = getattr(organisms, organism_name)
        gene_records = lb.Gene.from_values(
            df.index, field=lb.Gene.ensembl_gene_id, organism=organism_record
        )
        ln.save(gene_records)
        validated = lb.Gene.validate(
            df.index, field=lb.Gene.ensembl_gene_id, organism=organism_record
        )
        # register legacy genes manually
        new_records = []
        for gene_id in df.index[~validated]:
            new_records.append(
                lb.Gene(
                    ensembl_gene_id=gene_id,
                    symbol=df.loc[gene_id][1],
                    organism=organism_record,
                )
            )
        ln.save(new_records)

        genes_feature_set = ln.FeatureSet(
            features=gene_records + new_records,
            name=f"all {organism_record.name} genes",
        )
        genes_feature_set.save()
