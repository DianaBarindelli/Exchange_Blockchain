pragma solidity ^0.5.17;

import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/math/SafeMath.sol";

contract owned {
    address payable owner;
    mapping (address => uint) public balances;
    constructor () public payable{
        owner = msg.sender;
        balances[owner]+=msg.value;
    }
    modifier onlyOwner {
        require (msg.sender == owner, "Only the contract owner can call this function");
        _;
    }
}

contract mortal is owned{
    function destroy() public onlyOwner{
        selfdestruct(owner);
    }
}

contract Faucet is mortal {

    event Deposited(address people, uint256 quantity, uint256 time);

    function withdraw(uint withdraw_amount) public {
                
        require(address(this).balance>= withdraw_amount, 'Non ci sono fondi');
        msg.sender.transfer(withdraw_amount);
        
    }

    function deposit() external payable {
        require(msg.value!=0, "Please deposit an amount >0.");
        emit Deposited(msg.sender, msg.value, now);
    }


}

