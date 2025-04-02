require("@nomicfoundation/hardhat-toolbox");

const SKALE_ENDPOINT = "https://testnet.skalenodes.com/v1/lanky-ill-funny-testnet";
const PRIVATE_KEY = "d6795c913606efc3b717b90514cbf40b666537585c6d30b019de3fcc4f17d5f6";

module.exports = {
  solidity: "0.8.19",
  networks: {
    skale: {
      url: SKALE_ENDPOINT,
      accounts: [PRIVATE_KEY]
    }
  },
  paths: {
    sources: "./contracts",
    artifacts: "./artifacts"
  }
};