# QUDA
QUDA Question under Discussion Annotation Tool.

QUDA is a webserver annotation tool for NL texts in the context of QUD Theory and informational element classification.

This tool has been implemented and is being extended for the DFG funded Project 
"Propositional and Non-at-issue Content in Text Generation: Exploring the QUD–Perspective".

The App is a Django-based webapp, that can be deployed on a server using e.g. gunicorn and 
nginx in order to make it publicly available. It can also be used offline on a local computer.

QUDA offers a UI for creating QUD trees and classifications. It provides functions for
creating and deleting elements, shift in linear precedence, copy pasting and rebranching
of subbranches, classification of foci, topic etc.

The UI provides a window toggle, such that either one annotation, two annotations in parallel
or an annotation and a separate txt file can be viewed.

Export format is XML. The files are validated according to project internal annotation guidelines,
which are adapted from Riester et al., 2019.

The access rights are managed by an app admin, which may add credentials for new users.

The app uses server side cookies, which necessitate the storage of a cookie containing the session  ID
in the user's browser.

The app does not need storage on the host server, since files are uploaded to the app from the client
and the resulting XML downloaded to the latter for persistent storage. Between upload and download,
file handles are deleted and data / annotation progress is exceptionally stored in serverside cookies.
These cookies expire after logout.


Author:      Maurice Langner, M.A.
Email:       Maurice.Langner@rub.de / langner@linguistics.rub.de
affiliation: Ruhr-Universität Bochum
