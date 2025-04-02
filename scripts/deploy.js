const hre = require("hardhat");

async function main() {
  console.log("Deploying XineteStorage contract...");

  const XineteStorage = await hre.ethers.getContractFactory("XineteStorage");
  const xineteStorage = await XineteStorage.deploy();

  await xineteStorage.waitForDeployment();
  const address = await xineteStorage.getAddress();

  console.log("XineteStorage deployed to:", address);
  return address;
}

main()
  .then((address) => {
    console.log("Deployment successful!");
    process.exit(0);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });