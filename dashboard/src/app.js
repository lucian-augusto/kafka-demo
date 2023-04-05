const express = require("express")
const app = express();
const path = require("path");
const { Kafka } = require("kafkajs")
const clientId = "dashboard"
const brokers = ["kafka-broker:9092"]
const kafka = new Kafka({ clientId, brokers })
const consumer = kafka.consumer({ groupId: clientId })
const producer = kafka.producer()


const hostname = "0.0.0.0";
const port = 3000;

const run = async () => {
  await consumer.connect()
  await consumer.subscribe({ topics: ["invoice-generated", "score-calculated"], fromBeginning: true })

  await consumer.run({
    eachMessage: async ({ topic, message }) => {
      console.log({
        topic,
        offset: message.offset,
        value: message.value.toString(),
      })
    },
  })
}

run().catch(console.error());

app.get("/", function (req, res) {
  res.sendFile(path.join(__dirname, "../public/index.html"));
});

app.get("/invoice/generate", function (req, res) {
  const send = async () => {
    await producer.connect()
    await producer.send({
      topic: "generate-invoice",
      messages: [
        { value: "Hello KafkaJS user2!" },
      ],
    })
  }
  send().catch(console.error())
  res.redirect("/");
});

app.get("/score/calculate", function (req, res) {
  const send = async () => {
    await producer.connect()
    await producer.send({
      topic: "calculate-score",
      messages: [
        { value: "Hello KafkaJS user2!" },
      ],
    })
  }
  send().catch(console.error())
  res.redirect("/");
})

app.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});
