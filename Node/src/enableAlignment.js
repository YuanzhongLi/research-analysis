const fs = require('fs');
const { FREELIST_SPACE_PATH } = process.env;


try {
  const file = fs.readFileSync(
    FREELIST_SPACE_PATH,
    "utf8"
  );

  console.log(file);

  // const schemaArray: string[] = schema.split("\n");
  // const newSchema: string = schemaArray
  //   .map((t) => {
  //     if (t.includes("@searchable")) {
  //       return "  # @searchable";
  //     }
  //     return t;
  //   })
  //   .join("\n");

  // fs.writeFileSync(
  //   "amplify/backend/api/ReviewBankGql/schema.graphql",
  //   newSchema
  // );
} catch (err) {
  console.error(err);
}
