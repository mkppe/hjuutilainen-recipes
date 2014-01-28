#!/usr/bin/env python
#
# Copyright 2013 Hannes Juutilainen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urllib2
import json

from autopkglib import Processor, ProcessorError


__all__ = ["OnePasswordURLProvider"]

UPDATE_URL = "https://app-updates.agilebits.com/check/1/13.0.0/OPM4/en/400600"
DEFAULT_SOURCE = "Amazon CloudFront"


class OnePasswordURLProvider(Processor):
    """Provides a download URL for the latest 1Password"""
    input_variables = {
        "base_url": {
            "required": False,
            "description": "The 1Password update check URL",
        },
        "source": {
            "required": False,
            "description": "Where to download the disk image. "
            "Possible values are 'Amazon CloudFront', 'CacheFly' and 'AgileBits'. "
            "Default is Amazon CloudFront."
        }
    }
    output_variables = {
        "url": {
            "description": "URL to the latest 1Password release.",
        },
    }
    description = __doc__
    
    def download_update_info(self, base_url):
        """Downloads the update url and returns a json object"""
        try:
            f = urllib2.urlopen(base_url)
            json_data = json.load(f)
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))

        return json_data

    def get_1Password_dmg_url(self, base_url, preferred_source):
        """Find and return a download URL"""
        
        self.output("Preferred source is %s" % preferred_source)
        
        # 1Password update check gets a JSON response from the server.
        # Grab it and parse...
        info_plist = self.download_update_info(base_url)
        version = info_plist.get('version', None)
        self.output("Found version %s" % version)
        
        sources = info_plist.get('sources', [])
        found_source = next((source for source in sources if source['name'] == preferred_source), None)
        if found_source:
            source_url = found_source.get('url', None)
            if not source_url:
                raise ProcessorError("No URL found for %s" % preferred_source)
            return source_url
        else:
            raise ProcessorError("No download source for %s" % preferred_source)
    
    def main(self):
        base_url = self.env.get("base_url", UPDATE_URL)
        source = self.env.get("source", DEFAULT_SOURCE)
        self.env["url"] = self.get_1Password_dmg_url(base_url, source)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = OnePasswordURLProvider()
    processor.execute_shell()