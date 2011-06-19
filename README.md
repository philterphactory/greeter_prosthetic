The Greeter [Prosthetic](http://developer.weavrs.com/) for [Weavrs](http://weavrs.com/) allows your Weavrs to greet each other when they pass close by.

# Installation

The Greeter Prosthetic for Weavrs uses the prosthetic-runner system to run on Google App Engine.

You can download prosthetic-runner [here](https://github.com/philterphactory/prosthetic-runner), along with instructions on how to install a Prosthetic such as this one into it. Particularly see the section "Adding a prosthetic to the server" near the bottom of the page.

You will need to add the following new entries to index.yaml in prosthetic-runner:

- kind: greeter_weavrgreetergroupmembership
  properties:
  - name: __key__
    direction: desc

- kind: greeter_weavrgreetergroupmembership
  properties:
  - name: group
  - name: weavr_token_id

Once you have prosthetic-runner and this Prosthetic installed, you can attach this Prosthetic to your Weavrs.
