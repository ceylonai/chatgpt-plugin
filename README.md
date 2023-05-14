# chatgpt-plugin

Forget the hassle of designing openapi.yml - our project automatically generates it for you!

## Setup 
![Original Link](https://github.com/openai/plugins-quickstart)

To install the required packages for this plugin, run the following command:
```
pip install -r requirements.txt
```

To run the plugin, enter the following command:

```
python main.py
```

Once the local server is running:

- Navigate to https://chat.openai.com.
- In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
- Select "Plugin store"
- Select "Develop your own plugin"
- Enter in localhost:5003 since this is the URL the server is running on locally, then select "Find manifest file".

The plugin should now be installed and enabled! You can start with a question like "What is on my todo list" and then try adding something to it as well!
Getting help

If you run into issues or have questions building a plugin, please join our Developer community forum.
