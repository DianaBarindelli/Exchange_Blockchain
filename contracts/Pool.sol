pragma solidity 0.5.17;

import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Mintable.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Detailed.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/token/ERC20/ERC20Burnable.sol";

import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/access/roles/MinterRole.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/access/Roles.sol";
import "OpenZeppelin/openzeppelin-contracts@2.5.0/contracts/math/SafeMath.sol";


    /**
     *
     * This is the smart contract for the liquidity pool.
     * All the functions defined own a specific comment in order to
     * easily go through the code. there are some global variable
     * autoexplained which are used many times during the smart contract.
     *
     * The logic process in order to start using the liquidity is:
     *
     * 1. Deploy Token and Paycoins used in the liquidity pool
     * 2. Deploy the Pool defining (in the constructor) the token's
     * and paycoin's address which must be present in the liquidity.
     * 3. Mint token and paycoins to the liquidity from paycoin's and
     * token's owner.
     * 4. Call pool_Set function in order to set alle the variables
     * needed for the code.
     * 5. Enjoy.
     *
     * Note:
     *
     * Pool is TimeMarket which is a modifier used to check if the
     * market is openned or not. The market is open from 9a.m. to
     * 6p.m.
     *
     */


contract TimeMarket {

    uint256 closingTime;
    
    modifier TimeMarket() {

        require (MarketOpen(), "Market opening times 9.00 - 18.00");
        _;

    }

    function MarketOpen() public view returns(bool) {

        uint256 time=block.timestamp % (1 days);
        return (time > 7 hours ) && (time < 16 hours);


    }

}

contract Token is ERC20, ERC20Mintable, ERC20Detailed, ERC20Burnable {
    constructor (string memory name, string memory symbol, uint8 decimals) ERC20Detailed(name, symbol, decimals) public {}

}

interface POOLIF{

    function pool_Set() external;

    function set_K() external;
    
    function increase_Token(uint256 token_ToAdd) external;
    
    function decrease_Token(uint256 token_ToSub) external;
    
    function paycoins_neede_to_increase_Token(uint256 token_ToAdd) external view returns(uint256);
    
    function buy(uint256 token_Out) external;
    
    function sell(uint256 token_In) external;

    function TokenAddress() external view returns (address);
    
    function GetK() external view returns(uint256);
    
    function GetAddress() external view returns (address);
    
    function Get_Token_Price(uint256 token_Out) external view returns (uint256);
    
    function How_Many_Token(uint256 paycoin_In) external view returns (uint256);
    
    function Get_Paycoin_Price(uint256 paycoin_Out) external view returns (uint256);
    
    function How_Many_Paycoin (uint256 token_In) external view returns (uint256);

    function destruct() external;
    
    function Minting_Token(uint256 quantity) external;

}

contract Pool is MinterRole, TimeMarket{

    address _token;
    address _paycoin;
    address _owner; 

    IERC20 token_IF;
    IERC20 paycoin_IF;

    uint256 K;
    uint256 max_increase_decrease_amount;

    bool is_setted;

    event Bought(address buyer, uint256 token_out, uint256 paycoin_in, uint256 fees, uint256 time);
    event Sold(address seller, uint256 token_in, uint256 paycoin_out, uint256 fees, uint256 time);
    event Swapp(address swapper, uint256 token_out, uint256 token_in, uint256 fees, uint256 time);
    event Increase(uint256 token_increase, uint256 time);
    event Decrease(uint256 token_decrease, uint256 time);

    constructor (address token_address, address paycoin_address) public {

        _token= token_address;
        _paycoin= paycoin_address;
        token_IF = IERC20 (_token);
        paycoin_IF = IERC20(_paycoin);

        is_setted=false;

        _owner= msg.sender;
    }

        /**
     *
     * This is the function required to set K value and max_increase_decrease_amount
     * value. It must be called after the pool is deploied and after
     * paycoins and tokens are minted to the pool.
     *
     * A modifier is created in order to check if K value and
     * max_increase_decrease_amount are setted. It is extremely usfuel for
     * the calling of increase_Token, sell and swapp functions.
     *
     * Requirements:
     *
     * - is_setted is equal to false: if not the pool was already
     * setted.
     *
     */

    modifier pool_is_setted()   {

        require( is_setted == true, "Pool is still not setted");
        _;

    }

    function pool_Set() public onlyMinter {

        require (is_setted == false, "Pool is already setted");
        max_increase_decrease_amount = SafeMath.div(SafeMath.mul(token_IF.balanceOf(address(this)),50),100);        //50% del valore
        K=SafeMath.mul(token_IF.balanceOf(address(this)), paycoin_IF.balanceOf(address(this)));
        is_setted = true;
        
    }

    /**
     *
     * Function set_K, is the function used to set the constant which
     * define token price with hyperbole rule.
     * K was already setted in pool_set() function, but another function
     * is need after increase_Token and decrease_Token functions are
     * called
     *
     * Requirements:
     *
     * - No requirements needed.
     *
     */


    function set_K() public onlyMinter {

        K=SafeMath.mul(token_IF.balanceOf(address(this)), paycoin_IF.balanceOf(address(this)));

    }
        
    
    /**
     *
     * Function increase_Token, increase the token's balance of the
     * liquidity pool. The tokens are added without changing the token's
     * price calculated as the division between token's balance and
     * paycoin's balance. That's why, paycoin_ToAdd is calculated
     * and requested in this function.
     *
     * This function Emits a {Increase} event indicating how many
     * tokens are incremented in the liquidity pool and the time of
     * the transaction.
     *
     *
     * Requirements:
     *
     * - msg.sender must be Minter.
     * - the pool must have allowance for token_ToAdd, the msg.sender
     * wants to increase.
     * - the pool must have allowance for messanger's paycoin request
     * to increase token amount.
     * - token_ToAdd must not be more than max_increase_decrease_amount
     * which was setted as the 50% of the initial token amount.
     * - pool_is_setted, if not max_increase_decrease_amount is not setted.
     *
     */

    function increase_Token(uint256 token_ToAdd) public onlyMinter pool_is_setted{
        
        require(token_ToAdd < max_increase_decrease_amount, "max_increase_decrease_amount exceeded");
        
        //uint256 M = SafeMath.div(token_IF.balanceOf(address(this)), paycoin_IF.balanceOf(address(this)));
        //uint256 new_paycoin_amount = SafeMath.div(SafeMath.add(token_IF.balanceOf(address(this)), token_ToAdd), M);
        uint256 new_paycoin_amount = SafeMath.div(SafeMath.mul(SafeMath.add(token_IF.balanceOf(address(this)),token_ToAdd),paycoin_IF.balanceOf(address(this))),token_IF.balanceOf(address(this)));
        uint256 paycoin_ToAdd = SafeMath.sub(new_paycoin_amount, paycoin_IF.balanceOf(address(this)));
        
        token_IF.transferFrom(msg.sender, address(this), token_ToAdd);
        paycoin_IF.transferFrom(msg.sender, address(this), paycoin_ToAdd);
        
        emit Increase(token_ToAdd, now);
        
        set_K();
    }

    /**
     *
     * Function decrease_Token, decrease the token's balance of the
     * liquidity pool. The tokens are taken away without changing the
     * token's price calculated as the division between token's
     * balance and paycoin's balance. That's why, paycoin_ToSub is
     * calculated in this function and send to the mittent.
     *
     * This function Emits a {Decrease} event indicating how many
     * tokens are taken away from in the liquidity pool and the
     * time of the transaction.
     *
     *
     * Requirements:
     *
     * - msg.sender must be Minter.
     * - token_ToSub must not be more than max_increase_decrease_amount
     * which was setted as the 50% of the initial token amount.
     * - pool_is_setted, if not max_increase_decrease_amount is not setted.
     *
     */

    function decrease_Token(uint256 token_ToSub) public onlyMinter pool_is_setted{
        
        require(token_ToSub < max_increase_decrease_amount, "max_increase_decrease_amount exceeded");
        
        //uint256 M = SafeMath.div(token_IF.balanceOf(address(this)), paycoin_IF.balanceOf(address(this)));
        //uint256 new_paycoin_amount = SafeMath.div(SafeMath.sub(token_IF.balanceOf(address(this)), token_ToSub), M);
        uint256 new_paycoin_amount = SafeMath.div(SafeMath.mul(SafeMath.sub(token_IF.balanceOf(address(this)),token_ToSub),paycoin_IF.balanceOf(address(this))),token_IF.balanceOf(address(this)));
        uint256 paycoin_ToSub = SafeMath.sub(paycoin_IF.balanceOf(address(this)), new_paycoin_amount);
        
        token_IF.transfer(msg.sender, token_ToSub);
        paycoin_IF.transfer(msg.sender, paycoin_ToSub);
        
        emit Decrease(token_ToSub, now);
        
        set_K();
    }

    /**
     *
     * Function paycoins_neede_to_increase_Token, is used to show how
     * many paycoins the sender need to add in order to increase
     * token's balance of the pool of token_ToAdd amount.
     *
     * Requirements:
     *
     * - msg.sender must be Minter.
     * - token_ToAdd must not be more than max_increase_decrease_amount
     * which was setted as the 50% of the initial token amount.
     * - pool_is_setted, if not max_increase_decrease_amount is not setted.
     *
     */


    function paycoins_needed_to_increase_Token (uint256 token_ToAdd) public view onlyMinter pool_is_setted returns (uint256) {

        require (token_ToAdd < max_increase_decrease_amount, "max_increase_decrease_amount exceeded");
        uint256 M = SafeMath.div(token_IF.balanceOf(address(this)), paycoin_IF.balanceOf(address(this)));
        uint256 new_paycoin_amount = SafeMath.div(SafeMath.add(token_IF.balanceOf(address(this)), token_ToAdd), M);
        uint256 paycoin_ToAdd = SafeMath.sub(new_paycoin_amount, paycoin_IF.balanceOf(address(this)));

        return paycoin_ToAdd;

    }

    /**
     * Function buy is the function to buy some token from a
     * pool with paycoins. It requires token's quantity which are required
     * by the msg.sender.
     * The token's price are calculated with Uniswap rule
     * to be on hyperbole.
     *
     * Transaction fee are sended to the Pool's owner.
     * This function Emits a {Buy} event indicating buyer's address,
     * the quantity of token bought and the time of the transaction
     *
     * Requirements:
     *
     * - the pool must have allowance for messanger's paycoin for
     *   at least token's price and transaction fee.
     *
     */


    function buy (uint256 token_Out) public {

        uint256 new_token_amount = SafeMath.sub(token_IF.balanceOf(address(this)), token_Out);
        uint256 new_paycoin_amount = SafeMath.div(K, new_token_amount);
        uint256 paycoin_In= SafeMath.sub(new_paycoin_amount, paycoin_IF.balanceOf(address(this)));

        uint256 fee = SafeMath.div(SafeMath.mul(paycoin_In,3),1000);
        paycoin_IF.transferFrom(msg.sender,address(this),paycoin_In+fee);

        paycoin_IF.transfer(_owner, fee);
        token_IF.transfer(msg.sender,token_Out);

        emit Bought(msg.sender, token_Out, (paycoin_In+fee), fee, now);

    }

    /**
     * Function sell is the function to sell some tokens to the pool
     * in exchange for paycoins. Itrequires token's quantity that the
     * msg.sender wants to sell.
     * The token's price are calculated with Uniswap rule
     * to be on hyperbole.
     *
     * Transaction fee are sended to the Pool's owner.
     * This function Emits a {Sell} event indicating seller's address,
     * the quantity of token sold and the time of the transaction
     *
     * Requirements:
     *
     * - the pool must have allowance for messanger's token for
     *   at least token's price and transaction fee.
     * - pool_is_setted, if not the pool will give out all its
     * paycoins.
     *
     */

    function sell(uint256 token_In) public pool_is_setted{
        
        uint256 new_token_amount = SafeMath.add(token_IF.balanceOf(address(this)), token_In);
        uint256 new_paycoin_amount = SafeMath.div(K, new_token_amount);
        uint256 paycoin_Out=SafeMath.sub(paycoin_IF.balanceOf(address(this)),new_paycoin_amount);
        
        uint256 fee = SafeMath.div(SafeMath.mul(paycoin_Out, 3), 1000); 
        uint256 paycoin_Out_toB = SafeMath.sub(paycoin_Out,fee);
        
        token_IF.transferFrom(msg.sender, address(this), token_In);
        paycoin_IF.transfer(_owner, fee);
        paycoin_IF.transfer(msg.sender, paycoin_Out_toB);
        
        emit Sold(msg.sender, token_In, paycoin_Out_toB, fee, now);
    }

    /**
     * Function swapp is the function used from a msg.sender to exchange
     * some token of this pool he owned, with some token of a different
     * pool (named poolB). There is a double exchange between this pool
     * and poolB, and between this pool and msg.sender.
     * The token's price are calculated with Uniswap rule
     * to be on hyperbole.
     *
     * Transaction fee are sended to the Pool's owner: both for this pool
     * and poolB
     * This function Emits a {Swap} event indicating swapper's address,
     * the quantity of poolB's token required and the time of the transaction
     *
     * Requirements:
     *
     * - the pool must have allowance for messanger's token for
     *   at least token's price and transaction fee.
     * - pool_is_setted: if not, the pool will give out all of its
     * paycoions.
     *
     */



    function swap(address poolB_address, uint256 tokenB_requested) external pool_is_setted{
    
        POOLIF poolB_IF = POOLIF(poolB_address);
        IERC20 tokenB_IF = IERC20(poolB_IF.TokenAddress());
        
        uint256 new_token_amount_B = SafeMath.sub(tokenB_IF.balanceOf(poolB_IF.GetAddress()),tokenB_requested);
        uint256 paycoin_requested_B = SafeMath.sub(SafeMath.div(poolB_IF.GetK(), new_token_amount_B), paycoin_IF.balanceOf(poolB_IF.GetAddress()));
        uint256 paycoin_requestd_B_fee = SafeMath.div(SafeMath.mul(paycoin_requested_B, 3), 1000);
        
        uint256 paycoin_total_B = SafeMath.add(paycoin_requested_B, paycoin_requestd_B_fee);
        
        uint256 fee_A = SafeMath.div(SafeMath.mul(paycoin_total_B, 3), 1000);
        uint256 new_paycoin_amount_A = SafeMath.sub(paycoin_IF.balanceOf(address(this)), SafeMath.add(paycoin_total_B, fee_A) );
        
        uint256 new_token_amount_A = SafeMath.div(K, new_paycoin_amount_A);
        uint256 tokenA_In = SafeMath.sub(new_token_amount_A, token_IF.balanceOf(address(this)));
        
        token_IF.transferFrom(msg.sender, address(this), tokenA_In);
        paycoin_IF.transfer(_owner, fee_A);
        
        paycoin_IF.approve(poolB_IF.GetAddress(), paycoin_total_B);
        poolB_IF.buy(tokenB_requested); 
        tokenB_IF.transfer(msg.sender, tokenB_requested);
    
        emit Swapp(msg.sender, tokenB_requested, tokenA_In, fee ,now);
    
    }

    /**
     * Function Get_Token_Price is the function used to see how many
     * paycoins are required in order to get some token out of the
     * pool.
     *
     * Requirements:
     *
     * - No requirements needed.
     *
     */

    function Get_Token_Price(uint256 token_Out) public view returns (uint256){
    
        uint256 new_token_amount = SafeMath.sub(token_IF.balanceOf(address(this)), token_Out);
        uint256 new_paycoin_amount=SafeMath.div(K, new_token_amount);
        uint256 paycoin_In=SafeMath.sub(new_paycoin_amount, paycoin_IF.balanceOf(address(this)));
        uint256 fee = SafeMath.div(SafeMath.mul(paycoin_In, 3), 1000);
        uint256 total_coin_required=paycoin_In+fee;
        
        return total_coin_required;

    }

    /**
     * Function How_Many_Token is the function used to see how many
     * tokens are returned if i give some paycoins to the liquidity
     * pool.
     *
     * Requirements:
     *
     * - No requirements needed.
     *
     */

    function How_Many_Token(uint256 paycoin_In) public view returns (uint256){
    
        uint256 fee = SafeMath.div(SafeMath.mul(paycoin_In, 3), 1000);
        uint256 new_paycoin_amount = SafeMath.sub(SafeMath.add(paycoin_IF.balanceOf(address(this)), paycoin_In), fee);
        uint256 new_token_amount = SafeMath.div(K, new_paycoin_amount);
        uint256 token_returned= SafeMath.sub(token_IF.balanceOf(address(this)), new_token_amount);
        
        return token_returned;

    }

    /**
     * Function Get_Paycoin_Price is the function used to see how many
     * tokens the liquidity pool wants to get paycoin_Out paycoins of it's
     * paycoin's amount.
     *
     * Requirements:
     *
     * - No requirements needed.
     *
     */

    function Get_Paycoin_Price(uint256 paycoin_Out) public view returns (uint256){
    
        uint256 fee = SafeMath.div(SafeMath.mul(paycoin_Out, 3), 1000);
        uint256 new_paycoin_amount = SafeMath.sub(paycoin_IF.balanceOf(address(this)), SafeMath.sub(paycoin_Out, fee));
        uint256 new_token_amount = SafeMath.div(K, new_paycoin_amount);
        uint256 token_required = SafeMath.sub(new_token_amount, token_IF.balanceOf(address(this)));
    
        return token_required;
    
    }

    /**
     * Function How_Many_Paycoin is the function used to see how many
     * paycoins are returned by the liquidity pool, if token_In
     * token are sold.
     *
     * Requirements:
     *
     * - No requirements needed.
     *
     */

    function How_Many_Paycoin (uint256 token_In) public view returns (uint256){
    
        uint256 new_token_amount = SafeMath.add(token_IF.balanceOf(address(this)), token_In);
        uint256 new_paycoin_amount = SafeMath.div(K, new_token_amount);
        uint256 paycoin_Out=SafeMath.sub(paycoin_IF.balanceOf(address(this)),new_paycoin_amount);
        
        uint256 fee = SafeMath.div(SafeMath.mul(paycoin_Out, 3), 1000);
        uint256 paycoin_Out_toB = SafeMath.sub(paycoin_Out,fee);
        
        return paycoin_Out_toB;

    }

    /**
     * Function get_swapp_price is the function used to see how many
     * tokenA are needed in order to swapp them with tokenB_requested
     * tokens of poolB at the address poolB_addres.
     *
     * Requirements:
     *
     * - No requirements needed.
     *
     */

    function get_swap_price(address poolB_address, uint256 tokenB_requested) public view pool_is_setted returns(uint256){  //con una p sola
    
        POOLIF poolB_IF = POOLIF(poolB_address);
        IERC20 tokenB_IF = IERC20(poolB_IF.TokenAddress());
        
        uint256 new_token_amount_B = SafeMath.sub(tokenB_IF.balanceOf(poolB_IF.GetAddress()),tokenB_requested);
        uint256 paycoin_requested_B = SafeMath.sub(SafeMath.div(poolB_IF.GetK(), new_token_amount_B), paycoin_IF.balanceOf(poolB_IF.GetAddress()));
        uint256 paycoin_requestd_B_fee = SafeMath.div(SafeMath.mul(paycoin_requested_B, 3), 1000);
        
        uint256 paycoin_total_B = SafeMath.add(paycoin_requested_B, paycoin_requestd_B_fee);
        
        uint256 fee_A = SafeMath.div(SafeMath.mul(paycoin_total_B, 3), 1000);
        uint256 new_paycoin_amount_A = SafeMath.sub(paycoin_IF.balanceOf(address(this)), SafeMath.add(paycoin_total_B, fee_A) );
        
        uint256 new_token_amount_A = SafeMath.div(K, new_paycoin_amount_A);
        uint256 tokenA_In = SafeMath.sub(new_token_amount_A, token_IF.balanceOf(address(this)));
        
        return tokenA_In;
    
    }

    /**
     *
     * These are some useful functions that are used in Swapp function
     * in order to interact with poolB.
     *
     */
    

    function TokenAddress() external view returns (address) {return _token;}
    function GetK() external view returns (uint256) {return K;}
    function GetAddress() external view returns (address){return address(this);}

    /**
     *
     * I've no idea if someone will ever use this function, but that function
     * is implemented in the case the owner of the pool wants to destruct
     * his own liquidity pool.
     *
     */
    

    function destruct() external onlyMinter {
        selfdestruct;
    }

    function Minting_Token(uint256 quantity) public onlyMinter {
        Token _stonks = Token(_token);
        _stonks.mint(address(this), quantity);
    }

}







