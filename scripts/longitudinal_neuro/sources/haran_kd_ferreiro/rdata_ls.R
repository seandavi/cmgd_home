# Usage: Rscript --vanilla rdata_ls.R <file.RData> -- list objects (class, dim, names) without sourcing any code
f <- commandArgs(TRUE)[1]; e <- new.env(); nm <- load(f, envir = e)
for (n in nm) { o <- get(n, envir = e)
  d <- if (!is.null(dim(o))) paste(dim(o), collapse = "x") else length(o)
  cat(sprintf("%-40s %-25s %s\n", n, paste(class(o), collapse = ","), d))
  if (is.data.frame(o)) cat("   cols:", paste(head(names(o), 60), collapse = " | "), "\n")
}
