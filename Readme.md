# A mysteriously failing custom session interface for Flask

This is a reduced test case from failing functionality in a hybrid single-page web/PhoneGap application. Please don't be intimidated by the large number of files; this Readme serves to guide you to the relevant parts.

The issue is with a custom session interface, Flask's way to allow you to implement an alternative kind of session. In this case, we are trying to implement a server-side session that is completely cookie-free. The session data are stored in the same relational database as the application data. The session ID ("token") is passed explicitly in the HTTP request and response *bodies* (embedded in JSON data) and stored on LocalStorage by a custom JavaScript routine. Cookies must absolutely be avoided because *a PhoneGap application cannot store cookies*.

The custom session interface is defined in `reduced_testcase/server/session.py`. Please refer to [the Flask documentation](http://flask.pocoo.org/docs/0.10/api/#session-interface) for an explanation of what the session interface is supposed to do. The interface is enabled on line 30 of `reduced_testcase/__init__.py`. If you comment out that line (as it is by default when you clone this Gist), the application and the test suite use Flask's default cookie-only session interface instead.

The test suite contains seven (7) tests that all succeed with Flask's default session interface and all fail (or err) with our custom session interface. In all tests except for one (the exception being `test_bump` in `test_admin`), the problem appears to be that some key-value pairs are not retained on the session. This is mysterious, because the session object type is a subclass of Python's builtin `dict`. In the remaining test, there is no clear relation with the session interface whatsoever.

A stripped down version of the client side is included with this Gist. You may try the application as a user in order to get a feel for what it is supposed to do. Doing so, you will not notice a difference between the two session interfaces; in fact, the custom session interface appears to work exactly as intended in the application. Unfortunately, this is insufficient proof of correctness, especially given the fact that the tests are failing.

You do not need to read any of the code in `reduced_testcase/www`. This subfolder contains client-side code only. The problems related to the custom session interface are almost certainly entirely in the server-side Python parts of this Gist.

## Installation

 1. Clone this Gist to your local disk.
 2. Create a virtualenv, activate it and install the dependencies with  
     `pip install -r requirements.txt`
 3. By default, Flask's builtin cookie-based sessions are used. In order to switch to the custom session interface, uncomment line 30 of `reduced_testcase/__init__.py`.

## Running the tests

    python test.py

The test runner uses a memory-mapped SQLite database, so it doesn't leave any traces. You will get a lot of output when using the custom session interface.

## Trying the application

    python run.py

The first time you run the application, an empty SQLite database is created in `reduced_testcase/testcase.db`. You'll want to enter at least one "Brain Teaser" by visiting [http://localhost:5004/admin/brainteaser]. Make sure that it has a publication date in the past. You do not need to enter a closure date, but if you do, make sure that it lies in the future.

If you now go to the public interface at [http://localhost:5004/], you will see the brain teaser that you just created, except that it is now called a "Reflection". Think of it as a type of discussion topic. There is the option to reply anonymously and to moderate anonymous replies by other visitors.

## Expected behaviour

The application uses several heuristics to determine whether the visitor is human. One of those is the time interval between user-initiated requests. Normally the treshold is set to 200 milliseconds, i.e. if multiple user-initiated requests follow each other within 200 milliseconds then it is considered bot-like behaviour. However, since this is very difficult to test, the treshold has been set to 1 second in this Gist. Therefore, if you click two different buttons within 1 second, you'll be locked out of the application. You can fix this by erasing your cookies and LocalStorage and refreshing the page. As long as you wait at least 1 second between any two clicks on a moderation button or a submit button, you should not get blocked.

Normally, you'll receive a "thank you" for moderation votes. You can vote again on the same post if you refresh the page; this is by design.

You can send one reply without any need for authentication. If you reply again within ten minutes, you'll be presented with a notice that another reply has been received in the meanwhile (being your own previous reply). If you confirm and submit again, you are presented with a CAPTCHA. You will keep getting CAPTCHA challenges until you enter the correct answer.

## Sharing your insight

If you find the source of the problem, please answer [the associated question on StackOverflow](http://stackoverflow.com/questions/32483063/why-do-these-tests-fail-for-this-custom-flask-session-interface) so I can reward you. If you also find a workaround or even a real solution, please consider implementing it and pushing it to a fork of this Gist. Thank you very much in advance.
