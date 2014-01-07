py-wink ;-)
=======

Python library for interfacing with Wink devices, including:
- "Eggminder" eggtray
- "Nimbus" cloud_clock
- "Pivot Power Genius" powerstrip
- "Porkfolio" piggy_bank
- "Spotter" sensor_pod

This library implements the API at: http://docs.wink.apiary.io/

### Getting started

1. Get Oauth tokens to access the API.  The Wink API is currently in beta and
   not yet publicly available. However, you may request a set of tokens by
   emailing questions@quirky.com and asking for early access to the Wink API. 

2. Run the "login.py" script and provide your tokens and Wink account
   credentials.

3. Run the "test.py" script in interactive mode (`python -i test.py`) so you
   can interact with the Wink servers. All the test script does is fetch a list
   of your Wink devices, and print out the type and id for each.

### Requirements

- httplib2
- That's all, folks!

### Caveats

I only have a Nimbus "cloud_clock" and so far have only done a small amount of
testing. Any input, bug reports or additional functionality would be much
appreciated.

### Thanks

Thanks to Steven Shaw and everyone at Quirky for providing an API! Steven has
been really responsive in several forums over the last few weeks as they have
been rolling out the API. See this forum for more details:
http://www.quirky.com/forums/topic/21462
