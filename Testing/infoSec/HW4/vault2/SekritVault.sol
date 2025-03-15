// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SekritVault {
    string private secret;
    address private owner;
    bytes32[3] private data;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function set_data(bytes32[3] memory _data) public onlyOwner {
        data = _data;
    }

    function set_secret(string memory message) public onlyOwner {
        secret = message;
    }

    function get_secret(bytes32 _key) public view returns (string memory) {
        require(_key == data[0], "Invalid key");
        return secret;
    }
}
