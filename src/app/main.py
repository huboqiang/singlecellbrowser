import os
from flask import Flask, jsonify,render_template
from collections import Counter
from pymongo import MongoClient
import pymongo
import pandas as pd
import json
from flask_cors import CORS, cross_origin
import time

app = Flask(__name__,static_url_path='')
cors = CORS(app)
app.config['CORS_HEADERS'] = "Content-Type"


cluster_ip = os.getenv("CLUSTER_IP")
cluster_ip_mongo = os.getenv("CLUSTER_IP_MONGO")
cluster_port_mongo = os.getenv("CLUSTER_MONGO_PORT")
cluster_user_mongo = os.getenv("CLUSTER_MONGO_USER")
cluster_table_mongo = os.getenv("CLUSTER_MONGO_TABLE")
cluster_password_mongo =  os.getenv("CLUSTER_MONGO_PASSWORD")
cluster_api_port = os.getenv("CLUSTER_API_PORT")

cell_type_file = os.getenv("CELLTYPE_FILE")
cell_tpm_file  = os.getenv("CELLTPM_FILE")

client = MongoClient("mongodb://%s:%s@%s:%s/myCollection?authMechanism=SCRAM-SHA-1" % (cluster_user_mongo,cluster_password_mongo,cluster_ip_mongo,cluster_port_mongo))
postsExp = client[cluster_table_mongo].post

pd_hum_info = pd.read_csv(cell_type_file, index_col=[0])
f_gene = open(cell_tpm_file, "r")

pd_hum_info['sam'] = pd_hum_info.index
pd_hum_info['idxOrder'] = [i for i in range(pd_hum_info.shape[0])]
l_names = f_gene.readline().split("\t")
f_gene.close()


@app.route('/', methods = ['GET', 'POST'])
@cross_origin()
def hello_world():
    return render_template('index.html', CLUSTER_IP=cluster_ip, CLUSTER_API_PORT=cluster_api_port)

@app.route('/gene/<gene>', methods = ['GET', 'POST'])
@cross_origin()
def showTPM(gene):
    print(time.localtime())
    pd_genInfo = pd.DataFrame({"TPM" : postsExp.find_one({"gene" : gene})['exp'], "sam" : l_names[1:]})
    pd_genInfo.index = pd_genInfo['sam']
    pd_plot = pd_genInfo.join(pd_hum_info.drop(['sam'], axis=1)).dropna()
    #print(pd_plot.columns)
    pd_plot['group'] = pd_plot['group'].astype(int)
    l_r = ["sam,PC1,PC2,group,tissue,stage,type,idxOrder,TPM"]
    for row in pd_plot.iterrows():
        #print(row[1])
        l_r.append("%s,%1.3f,%1.3f,%d,%s,%s,%s,%d,%1.3f" % (row[1]['sam'],
                                                            row[1]['PC1'],row[1]['PC2'],
                                                            row[1]['group'],row[1]['tissue'],
                                                            row[1]['stage'],row[1]['type'],
                                                            row[1]['idxOrder'],row[1]['TPM']
                                                        ))

    print(time.localtime())
    return '\n'.join(l_r)

@app.route('/geneBox/<gene>', methods = ['GET', 'POST'])
@cross_origin()
def TPMBoxTypeStage(gene):
    pd_genInfo = pd.DataFrame({"TPM" : postsExp.find_one({"gene" : gene})['exp'], "sam" : l_names[1:]})
    pd_genInfo.index = pd_genInfo['sam']
    pd_plot = pd_genInfo.join(pd_hum_info.drop(['sam'], axis=1)).dropna()
    #print(pd_plot.columns)
    pd_plot['group'] = pd_plot['group'].astype(int)
    pd_plot['group'] = [ "10W" if x=="9WP" else x for x in pd_plot['group'] ]
    l_stages = ['5W', '6W', '7W', '8W', '9W', '11W', '13W', '17W', '23W', '24W']
    
    M_stageColor = {
              "5W" :   "#5E4FA2",
              "6W" :   "#3682BA",
              "7W" :   "#5CB7A9",
              "8W" :   "#D0EC9C",
              "9W" :   "#F3FAAD",
              "11W" :   "#FEF0A7",
              "13W" :   "#FDCD7B",
              "17W" :   "#FA9C58",
              "23W" :   "#EE6445",
              "24W" :   "#D0384D"
    }

    l_json = []
    for stageUsed in l_stages:
        pd_plotSub = pd_plot[pd_plot['stage']==stageUsed]
        M_info = {
            "y" : list(pd_plotSub['TPM'].values),
            "x" : list(pd_plotSub['type'].values),
            "name" : stageUsed,
            "marker" : {
                "color" : M_stageColor[stageUsed]
            },
            "type" : 'box'
        }
        l_json.append(M_info)

    return jsonify(results=l_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
