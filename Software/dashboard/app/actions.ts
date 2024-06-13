"use server";
require("dotenv").config();
import { MongoClient, Db } from "mongodb";

var client: MongoClient | undefined;
var db: Db | undefined;
const connString = process.env.MONGO_URL;
if (connString == undefined)
  throw new Error("Can't Find Database Connection String");
else {
  client = new MongoClient(connString);
  db = client.db("smartgrid");
}

async function getTick(yValues: any) {
  var res = await db
    ?.collection("ticks")
    .find({}, { projection: { _id: 0, ...yValues, day: 1, tick: 1 } })
    .sort({
      day: 1,
      tick: 1,
    })
    .toArray();
  return res;
}

async function getDayAndTick(){
  const res = await fetch("https://icelec50015.azurewebsites.net/demand");
  const data = await res.json();
  return {
    day: data.day,
    tick: data.tick
  }
}

async function getValuesOnTick(yValues: any, day: number, tick: number) {
  var res = await db
    ?.collection("ticks")
    .findOne({tick: tick, day: day}, { projection: { _id: 0, ...yValues, day: 1, tick: 1 } });
  return res;
}


export { getTick, getDayAndTick, getValuesOnTick };
