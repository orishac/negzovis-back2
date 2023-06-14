# Dataset Files Management

### Requirements :

-   We want to accept up to 256MB of raw data, more than that and the Hugobot/Karmalego will not be able to handle it anyway.
-   FIles will have one time use when processing the dataset.
-   Users will be able to download the uploaded files on need.

### Conclusions:

-   When uploading files we will split the files to chunks and send the chunks in separate HTTP requests.
-   To save disk space the files will be zipped. It will not affect too much because using the files is only a one time thing.

### Upload process:

-   When uploading files the file will be sent in chunks.
-   When the first chunk is received a metadata of the file will saved in the database with a unique identifier.
-   When the last chunk has been sent the file has a whole will be saved in a temporary folder and zipped.

### The dataset upload process:

-   Filling out the dataset info (name, category...) - Client side.
-   Upload of raw data, vmap and entities separately via the upload process.
-   Upload completion - validation of the form fields and files and moving the files to the dataset directories.

### Libraries:

We will be using a file uploader library in the frontend that will manage the the upload requests and chunking. The library is called DropZone and will use a wrapper for react called "react-dropzone-component". There is a chance that this wrapper library is not maintained any more but the popular library "react-dropzone" does not support chunking.

### Notes:

-   Make VMap optional and add the ability to add it manually or via a file later
