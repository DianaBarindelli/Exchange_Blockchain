pragma solidity ^0.5.0;

contract TimeMarket {
    uint256 closingTime;
    
    modifier TimeMarket() {
        require(MarketOpen(), "Market open 9.00 - 18.00");
        _;
    }
    
    function MarketOpen() public view returns(bool){
        uint256 time = block.timestamp % (1 days);
        return (time > 7 hours) && (time < 16 hours);
    }
}
