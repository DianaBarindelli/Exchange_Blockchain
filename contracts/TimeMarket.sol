pragma solidity ^0.5.17;

import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Mintable.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Detailed.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Burnable.sol";

import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/access/roles/MinterRole.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/access/Roles.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/math/SafeMath.sol";

// contract TimeMarket {

//     uint256 closingTime;
    
//     modifier TimeMarket() {

//         require (MarketOpen(), "Market opening times 9.00 - 18.00");
//         _;

//     }

//     function MarketOpen() public view returns(bool) {

//         uint256 time=block.timestamp % (1 days);
//         return (time > 7 hours ) && (time < 16 hours);


//     }

// }