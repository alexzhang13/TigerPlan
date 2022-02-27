const { PrismaClient } = require("@prisma/client")


const prisma = new PrismaClient()

// send queries to the database
async function main() {
  const allLinks = await prisma.link.findMany()
  console.log(allLinks)
}

main()
  .catch(e => {
    throw e
  })
  // close connection after script terminates
  .finally(async () => {
    await prisma.$disconnect()
  })