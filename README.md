# single cell results browser:

See [http://huboqiang.github.io/humanretina.html](http://huboqiang.github.io/humanretina.html) for an example.

## upload your own data

THIS PART is STILL DEVELOPING. 

In brief, two files should be prepared like `/src/app/Matrix_tSNE_type5.v2.csv` and `src/app/Merge.TPM.header.tsv`.

Then, change `scFlaskAPI.yaml` and `scFlaskFlask.yaml` for `CELLTYPE_FILE` and `CELLTPM_FILE`. 

Thirdly, as TPM file is too large, `src/app/Merge.TPM.header.tsv` need to be uploaded into mongodb service. just upload your data in a mongodb document with format:

```
{
    [gene1] = [exp_sam1, exp_sam2, ..., exp_samN],
    [gene2] = [exp_sam1, exp_sam2, ..., exp_samN],
    ...
    [geneM] = [exp_sam1, exp_sam2, ..., exp_samN],
}
```
Finally, revise `src/app/main.py` and `src/app/templates/index.html` to get better colors for each cell types. 

Also, you need to change

```
<script type="text/javascript" src="http://qcloud-1252801552.file.myqcloud.com/geneName.js"></script>
```

into your own gene-list file if you need your own gene lists. This file looks like:

```js
var options = ["5_8S_rRNA", "5S_rRNA", ... ]
```

## build your docker

After the revision of `src/app/main.py` and `src/app/templates/index.html`, please build your own docker images and push it into dockerhub or other private hubs.

```
docker build -t IP:PORT/PROJECT/NAME:VER src
docker push IP:PORT/PROJECT/NAME:VER
```

## deploy on a kubernetes cluster

When your data preparing was done, change `spec:template:spec:containers:env`  and `spec:template:spec:containers:image`  into your own value in `scFlaskAPI.yaml`, `scFlaskFlask.yaml` and `scFlaskMongodb.yaml`

Also change the `nodePort` value in `scFlaskAPISvc.yaml`, `scFlaskFlaskSvc.yaml` and `scFlaskMongodbSvc.yaml` file.

Run the command below in order:

```
for file in scFlaskMongodb.yaml scFlaskMongodbSvc.yaml scFlaskAPI.yaml scFlaskAPISvc.yaml scFlaskFlask.yaml scFlaskFlaskSvc.yaml
do
    kubectl create -f $file
done
```

Finally, go to your browser and type: `http://CLUSTER_IP:CLUSTER_INDEX_PORT` to browser your data.