pragma solidity 0.5.17;

import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Mintable.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Detailed.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Burnable.sol";

contract Token is ERC20, ERC20Mintable, ERC20Detailed, ERC20Burnable {
    constructor (string memory name, string memory symbol, uint8 decimals) ERC20Detailed(name, symbol, decimals) public {}

}
