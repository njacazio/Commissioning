# epn2raw

Note: the `en2raw.sh` script might work or not, it is not maintained. Use the `epn2raw.cc` and build it.

The `epn2raw` program needs to be built by hand
```
g++ -o epn2raw epn2raw.cc
```

Run it with
```
usage: ./epn2raw [filename.tf] [shift]
```
where `filename.tf` is the name of the file produced by the EPN. Notice that you need to have the `.info` file as well, otherwise there is no chance to convert to `.raw` format. The output of the program is a `.raw` file.

The `.info` file is necessary to have information about byte offsets to search for the raw data, but there have been occasions where the information in the `.info` file was not correct and a shift needed to be applied to actually find the data. It might need some experimentation in case, and the use of `shift` to add extra byte offsets (positive or negative).

Notice also that the program might not work, one possible reason is a consistency check that has been included some time ago. In case of troubles, remove this part from the `epn2raw.cc` file (or fix it) and rebuild
```
/** check for consistency **/
uint32_t *RDHs = reinterpret_cast<uint32_t *>(buffer);
if (*RDHs != 0x00044004) {
  printf(" --- wrong RDH signature at offset %ld : %08x \n ", offset, *RDHs);
  break;
}
```
The check is supposed to make sure that the beginning of the raw data record matches the expected RDH signature (first word of RDH).
If you run into this error, you might need to adjust the `shift`, or to adjust the signature in the code, or both.
