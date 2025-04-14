// Here is the file i run in my scriptfile
// I put what was ran in my script into a file vs typing it all out in the terminal :)

use acmeLoans

db.applications.insertOne({
  applicationNumber: "A1001",
  name: "Alice Johnson",
  zipcode: "55401",
  status: "received",
  notes: []
})

db.applications.updateOne(
  { applicationNumber: "A1001" },
  { $set: { status: "processing" } }
)

db.applications.updateOne(
  { applicationNumber: "A1001" },
  {
    $push: {
      notes: {
        type: "subphase",
        phase: "credit check",
        task: "Check FICO",
        message: "Passed with score 720",
        timestamp: new Date()
      }
    }
  }
)

db.applications.updateOne(
  { applicationNumber: "A1001" },
  { $set: { status: "accepted" } }
)

db.applications.updateOne(
  { applicationNumber: "A1001" },
  {
    $push: {
      notes: {
        type: "term",
        message: "Approved for $50,000 at 3.2% interest over 5 years",
        timestamp: new Date()
      }
    }
  }
)

db.applications.findOne({ applicationNumber: "A1001" })
