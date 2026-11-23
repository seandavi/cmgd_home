# Usage: Rscript --vanilla dump_rds_sampledata.R <in.rds|in.Rda> <out.tsv>
# Reads a serialized R object (data only; no downloaded code is sourced) and
# writes the phyloseq sample_data (or data.frame objects) as TSV.
args <- commandArgs(trailingOnly = TRUE)
f <- args[1]; out <- args[2]
get_sd <- function(o) {
  # attr() avoids loading the phyloseq class definitions (package not installed)
  if (!is.null(attr(o, "sam_data"))) o <- attr(o, "sam_data")
  if (!is.null(attr(o, "row.names")) && !is.null(attr(o, "names")) && isS4(o)) {
    d <- unclass(o); attributes(d) <- NULL
    df <- as.data.frame(setNames(d, attr(o, "names")), stringsAsFactors = FALSE)
    rownames(df) <- attr(o, "row.names")
    return(df)
  }
  if (is.data.frame(o)) return(o)
  NULL
}
if (grepl("\\.rds$", f, ignore.case = TRUE)) {
  objs <- list(obj = readRDS(f))
} else {
  e <- new.env(); nm <- load(f, envir = e); objs <- mget(nm, envir = e)
}
for (n in names(objs)) { o <- objs[[n]]; cat(n, class(o), "\n"); if (is.list(o) && !is.data.frame(o)) str(o, max.level = 1) }
sd <- NULL
for (o in objs) { sd <- get_sd(o); if (!is.null(sd)) break }
if (is.null(sd)) stop("no sample_data/data.frame found")
sd <- cbind(row_name = rownames(sd), sd)
write.table(sd, out, sep = "\t", quote = FALSE, row.names = FALSE, na = "")
cat("wrote", nrow(sd), "rows x", ncol(sd), "cols\n")
