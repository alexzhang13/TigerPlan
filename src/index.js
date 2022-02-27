const { ApolloServer } = require('apollo-server');
const { PrismaClient } = require('@prisma/client')

const typeDefs = `
  type Query {
    info: String!
  }
`
const resolvers = {
    Query: {
      info: () => null,
    }
  }

const prisma = new PrismaClient()

const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: {
    prisma,
  }
})

server
  .listen()
  .then(({ url }) =>
    console.log(`Server is running on ${url}`)
  );