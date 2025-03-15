// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SekritVault {
    address public owner;
    uint public current_user_count;
    string public secret;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function set_secret(string memory message) public onlyOwner {
        secret = message;
    }

    function increment_current_user_count(uint _count) public onlyOwner {
        current_user_count += _count;
    }

    function get_current_user_count() public view returns (uint) {
        return current_user_count;
    }

    function decrement_current_user_count(uint _count) public onlyOwner {
        current_user_count -= _count;
    }
}
