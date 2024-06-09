"use server";
require("dotenv").config();
import { MongoClient, Db } from "mongodb";
import { Variable, xValues } from "@/helpers/graph_data";

var client: MongoClient | undefined;
var db: Db | undefined;
const connString = process.env.MONGO_URL;
if (connString == undefined)
  throw new Error("Can't Find Database Connection String");
else {
  client = new MongoClient(connString);
  db = client.db("smartgrid");
}

async function getTick(prop: Variable) {
  var res = await db
    ?.collection(prop.collection)
    .find({}, { projection: { _id: 0, [prop.value]: 1, ...xValues } })
    .sort({
      day: 1,
      tick: 1,
    })
    .toArray();
  // console.log(res)
  return res;
}



async function getTicksAfter(day: number, tick: number, prop: Variable){
  var res = await db
    ?.collection(prop.collection)
    .find({ day: { $gt: day }, tick: { $gt: tick } }, { projection: { _id: 0, [prop.value]: 1, ...xValues } })
    .sort({
      day: 1,
      tick: 1,
    })
    .toArray();
  return res;
}


export { getTick, getTicksAfter };
