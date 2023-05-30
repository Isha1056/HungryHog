// solidity compiler version
// use solidity --version
// https://solidity.readthedocs.io/en/v0.4.24/layout-of-source-files.html#version-pragma
pragma solidity ^0.4.24;

// import library file  
// https://solidity.readthedocs.io/en/v0.4.24/layout-of-source-files.html#importing-other-source-files
// we should use libraries for common utility functions
//  source https://github.com/ethereum/dapp-bin/tree/master/library
// Library only compiled once and used again and again
import "stringUtils.sol";


contract reviewRecords {

    // enum type variable to store user gender
    // Actual user object which we will store
    // This similar to model/schema file in our Restful-app-backend 
    struct reviewRecord{
        string USER_EMAIL;
        string USER_NAME;
        string SNACK_ID;
        string SNACK_REVIEW;
        string SCHEDULE_DATE;
        uint SNACK_RATING;
    }
    
    mapping(string => reviewRecord[]) allRecords;

    // user object
    // you can also declare it public to access it from outside contract
    // https://solidity.readthedocs.io/en/v0.4.24/contracts.html#visibility-and-getters
    reviewRecord review_obj;

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
    function setReview(string USER_EMAIL, string USER_NAME, string SNACK_ID, string SNACK_REVIEW, string SCHEDULE_DATE, uint SNACK_RATING) public {
        review_obj = reviewRecord({
            USER_EMAIL:USER_EMAIL, USER_NAME: USER_NAME, SNACK_ID:SNACK_ID, SNACK_REVIEW: SNACK_REVIEW, SCHEDULE_DATE:SCHEDULE_DATE, SNACK_RATING:SNACK_RATING
        });

        allRecords[SNACK_ID].push(review_obj);

    }

    // get user public function 
    // This is similar to getting object from db.
    function getUserReview(string SNACK_ID, string USER_EMAIL, string SCHEDULE_DATE) public returns (string, uint) {
        for(uint i = 0; i < allRecords[SNACK_ID].length;  i++) {
            if(StringUtils.equal(allRecords[SNACK_ID][i].USER_EMAIL, USER_EMAIL) && StringUtils.equal(allRecords[SNACK_ID][i].SCHEDULE_DATE, SCHEDULE_DATE))
                return (
                    allRecords[SNACK_ID][i].SNACK_REVIEW, allRecords[SNACK_ID][i].SNACK_RATING
                );
        }
        return ("",uint(0));
    }

    function getReview(string SNACK_ID, uint INDEX) public returns (string, string, string, string, string, uint) {
        review_obj = allRecords[SNACK_ID][INDEX];
        return (
            review_obj.USER_EMAIL, review_obj.USER_NAME, review_obj.SNACK_ID, review_obj.SNACK_REVIEW, review_obj.SCHEDULE_DATE, review_obj.SNACK_RATING
        );
    }

    function get_array_length(string SNACK_ID) public returns (uint) {
        return allRecords[SNACK_ID].length;
    }
}