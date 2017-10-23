Scripts we use that may be helpful for others when stress testing with Locust.io

Right now there is only one test template, "simple_stress_single_page_with_args_from_csv" which stress tests a host with URLs provided from a CSV. Because of the way this test is set up it is meant to be used when you are hitting essentially one page with many different arguments or parameters.

## Installation

Just `pip install locust` (a virtualenv is recommended)

## Usage

Place a .csv containing the URL path and parameters in the same directory as the test locustfile.

Call `locust --host` and provide the hostname as the arguent. This may require sudo on \*nix system so the rlimit can be increased.

Example:

locust --host https://example.com

