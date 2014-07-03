Dispatch Web
============

Dispatch is an automated system which monitors directories for while and executes a file transfer when certain criteria are met. Currently, it only supports Aspera file transfers but it could be extended with FTP, SFTP or WebDav support. To create a custom poller, inherit from the PollerBase class and override the poll method.

Dispatch Web is a [Django](https://www.djangoproject.com/) web application that is the central web interface for controlling Dispatch agents. All configuration for the agents is stored in the local database. Agents poll for config changes and restart as neccessary. Logging and searching are provided on the interface as all transfers from the agents are logged centrally.

* Dispatch Web requires a database and web server. Included in the repository are Apache/mod_wsgi configurations.

Dispatch Agent is the stateless agent which actually monitors the directories and initiates the transfers. You can run and agent on the same server as Dispatch web, or scale out to multiple nodes.



