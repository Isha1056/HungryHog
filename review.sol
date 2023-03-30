// solidity compiler version
// use solidity --version
// https://solidity.readthedocs.io/en/v0.4.24/layout-of-source-files.html#version-pragma
pragma solidity ^0.4.21;

// import library file  
// https://solidity.readthedocs.io/en/v0.4.24/layout-of-source-files.html#importing-other-source-files
// we should use libraries for common utility functions
//  source https://github.com/ethereum/dapp-bin/tree/master/library
// Library only compiled once and used again and again
import "stringUtils.sol";


contract ReviewRecords {

    // enum type variable to store user gender
    // Actual user object which we will store
    // This similar to model/schema file in our Restful-app-backend 
    struct review{
        string USER_EMAIL;
        string USER_NAME;
        string SNACK_ID;
        string SNACK_REVIEW;
        string SNACK_RATING;
    }
    
    // user object
    // you can also declare it public to access it from outside contract
    // https://solidity.readthedocs.io/en/v0.4.24/contracts.html#visibility-and-getters
    review review_obj;

    // Internal function to conver genderType enum from string
    // function getGenderFromString(string gender) internal returns (genderType) {
    //     if(StringUtils.equal(gender, "male")) {
    //         return genderType.male;
    //     } else {
    //         return genderType.female;
    //     }
    // }

    // Internal function to conver genderType enum to string
    // function getGenderToString(genderType gender) internal returns (string) {
    //     if(gender == genderType.male) {
    //         return "male";
    //     } else {
    //         return "female";
    //     }
    // }

    // set user public function 
    // This is similar to persisting object in db.
    function setReview(string USER_EMAIL, string USER_NAME, string SNACK_ID, string SNACK_REVIEW, string SNACK_RATING) public {
        review_obj = user({
            USER_EMAIL:USER_EMAIL, USER_NAME: USER_NAME, SNACK_ID:SNACK_ID, SNACK_REVIEW: SNACK_REVIEW, SNACK_RATING:SNACK_RATING
        });
    }

    // get user public function 
    // This is similar to getting object from db.
    function getReview() public returns (string, string) {
        return (
            review_obj.USER_EMAIL, review_obj.USER_NAME, review_obj.SNACK_ID, review_obj.SNACK_REVIEW, review_obj.SNACK_RATING
        );
    }
}