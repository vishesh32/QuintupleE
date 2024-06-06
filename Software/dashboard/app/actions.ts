'use server'
require('dotenv').config()
import { MongoClient, Db } from 'mongodb'

var client: MongoClient | undefined;
var db: Db | undefined;
const conn_string = process.env.MONGO_URL
if(conn_string == undefined) throw new Error("Can't Find Database Connection String")
else {
    client = new MongoClient(conn_string);
    db = client.db("smartgrid")
}

async function getTick(prop: string){
    var res = await db?.collection("ticks-live").find({}, { projection: {_id: 0, [prop]: 1, tick: 1, day: 1} })
    .sort({
        "day": 1,
        "tick": 1
    })
    .toArray()
    // console.log(res)
    return res;
}

export { getTick }