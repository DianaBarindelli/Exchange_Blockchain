pragma solidity ^0.5.0;

import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/IERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Detailed.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Mintable.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/math/SafeMath.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/math/Math.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/ownership/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/access/roles/WhitelistedRole.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/access/roles/MinterRole.sol";
import "/home/cristiano/blockchain_test/challenge/contracts/token.sol"; //right path needed
//import "./token.sol";
import "./TimeMarket.sol";

// ***** DA AGGIUNGERE NUMERO MINIMO DI CHALLENGE *******


//contract Challenge is WhitelistedRole, TimeMarket {
contract Challenge is WhitelistedRole {
    
    using SafeMath for uint256;
	
    Token _paytoken; 

    uint256 _startTime; 
    address _target1; 
    address _target2;
    address _launcher;
    uint256 _challengeNumber;

    uint256 public constant _waitingTime = 20; // ... seconds 
    
    uint256 public constant _max1v1 = 10; // maximum number of 1v1 challenges
    uint256 public constant _max1v2 = 10; // maximum number of 1v2 challenges 
    mapping(address => uint256) _launched1v1; // to keep score of how many 1v1 challenges have been launched
    mapping(address => uint256) _launched1v2; // to keep score of how many 1v2 challenges have been launched

	event Challenge1v1Launched(
        uint256 challengeNum,
        address launcher,
        address target,
        uint256 launch_time
    );

	event Challenge1v2Launched(
        uint256 challengeNum,
        address launcher,
        address target1,
        address target2,
        uint256 launch_time
    );

    event ChallengeEnded(
        uint256 challengeNum,
        address winner,
        uint256 winning_time
    );

	constructor(address paytokenAddr, address [] memory allowlist) public {	
    	_paytoken = Token(paytokenAddr);

        addWhitelisted(allowlist[0]);
        addWhitelisted(allowlist[1]);
        addWhitelisted(allowlist[2]);
        addWhitelisted(allowlist[3]);
        addWhitelisted(allowlist[4]);

        //renounceOwnership(); 
	}
    
    // LAUNCHING FUNCTIONS

    function launch_1v1(address target)  onlyWhitelisted TimeMarket public {
    
        require(_startTime == 0, "A challenge has already been launched.");
        require(isWhitelisted(target), "You shall challenge only whitelisted");
        
        require(address(msg.sender) != address(target), "You shall not challenge yourself.");
        
        require(_launched1v1[msg.sender] < _max1v1, "Maximum challenges exceded.");
        // number of challenges has a limit
        _launched1v1[msg.sender] += 1;
		// increasing the number of challenges of the launcher

        _paytoken.transfer(msg.sender, 1000 * (10 ** _paytoken.decimals()));
        // reward for having started the challenge
        
        _launcher = address(msg.sender);
        _target1 = target;
        _startTime = now;
        _challengeNumber += 1;
        // countdown starts
        
        emit Challenge1v1Launched(_challengeNumber, _launcher, _target1, _startTime);
    }

    function launch_1v2(address target1, address target2)  onlyWhitelisted TimeMarket public {

        require(_startTime == 0, "A challenge has already been launched.");
        require(isWhitelist(target1), "You shall challenge only whitelisted");
        require(isWhitelist(target2), "You shall challenge only whitelisted");

        require(address(msg.sender) != address(target1) && address(msg.sender) != address(target2) && address (target1)!= address(target2), "You shall not challenge yourself OR the targets must be different addresses.");

        require(_launched1v2[msg.sender] < _max1v2, "Maximum challenges exceded.");
		// number of challenges has a limit
        _launched1v2[msg.sender] += 1;
		// increasing the number of challenges of the launcher        

        _paytoken.transfer(msg.sender, 2000 * (10 ** _paytoken.decimals()));
        // reward for having started the challenge

        _launcher = address(msg.sender);
        _target1 = target1;
        _target2 = target2;
        _startTime = now;
        _challengeNumber += 1;
        // countdown starts

        emit Challenge1v2Launched(_challengeNumber, _launcher, _target1, _target2, _startTime);
    }

    function accept() onlyWhitelisted TimeMarket public {
        
        require(msg.sender == _target1 || msg.sender == _target2 || msg.sender == _launcher , "You are not currently involved in a challenge.");
        //msg.sender must be the launcher or target
        
        require(_startTime != 0, "Every challenge already over.");

        uint256 endTime = _startTime + _waitingTime * 1 seconds; 

        if (now < endTime) { 
            revert("WAIT: the challenge is about to start!");
        }
        //20 seconds must elapse before anyone can respond
        
        else if (now > endTime){
            
            if (_target1 != address(0) && _target2 == address(0)){ 
                _paytoken.transfer(msg.sender, 10000 * (10 ** _paytoken.decimals()));
            }
            // challenge 1v1 had been launched: the reward is 10000
            
            else if (_target1 != address(0) && _target2 != address(0)){ // challenge 1v2 launched
                _paytoken.transfer(msg.sender, 50000 * (10 ** _paytoken.decimals()));
            }        
            // challenge 1v2 had been launched: the reward is 50000

            // now reset everything to close the challenge

            _launcher = address(0); // Reset sender
            _target1 = address(0); // Reset target
            _target2 = address(0);
            _startTime = 0; // Reset time
            endTime=0;

            emit ChallengeEnded(_challengeNumber, msg.sender, now);
        }
    }

    // checking the status of the challenge
    function checkChallengeStatus() public view returns (string memory){
        if(_launcher == address(0)){
            revert("CHALLENGE NOT ACTIVE");
        } 
        else if(_launcher != address(0)){
            revert("CHALLENGE ACTIVE");
        } 
    }
    
    // forcedClosure, callable by anyone, after 5 minutes from the end of a challenge
    // in order not to leave any challenge open (useful after calling checkChallengeStatus())
    function forcedClosure() onlyWhitelisted public { 
        require(now > _startTime + _waitingTime + 30 minutes);
        _launcher = address(0); // Reset sender
        _target1 = address(0); // Reset target
        _target2 = address(0);
        _startTime = 0; // Reset time
        emit ChallengeEnded(_challengeNumber, msg.sender, now);
    }


    // CONTROL FUNCTIONS
    
    // how many challenges left (1v1) (max is 10)
    function left1v1 (address id) public view returns (uint256) {
        return _max1v1 - _launched1v1[id];
    }

    // how many challenges left (1v2) (max is 10)
    function left1v2 (address id) public view returns (uint256) {
        return _max1v2 - _launched1v2[id];
    }
    
    // time to wait to accept the challenge
    function timeLeft() public view returns (uint256) {
        require(_startTime != 0, "Every challenge is already over!");
        uint256 endTime = _startTime + _waitingTime * 1 seconds; 
        return(endTime - now);
    }

}


    
