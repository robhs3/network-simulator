import tkinter as tk

root = tk.Tk()

root.title("Network Simulator")
root.geometry("1000x700")

selected_tool = None
node_count = 0

sidebar = tk.Frame(root, width=150, bg="darkgray")
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

canvas = tk.Canvas(root, bg="black")
canvas.pack(side="right", fill="both", expand=True)

def node_clicked(event):
    item = canvas.find_withtag("current")

    tags = canvas.gettags(item)

    print(tags)

def canvas_clicked(event):
    global selected_tool
    global node_count

    if selected_tool is None:
        return

    node_count += 1
    node_tag = f"node_{node_count}"

    if selected_tool == "host":
        canvas.create_rectangle(
            event.x - 30,
            event.y - 20,
            event.x + 30,
            event.y + 20,
            fill="lightblue",
            tags=("node", node_tag)
        )

        canvas.create_text(
            event.x,
            event.y,
            text="Host",
            tags=("node", node_tag)            
        )

    elif selected_tool == "switch":
        canvas.create_rectangle(
            event.x - 30,
            event.y - 20,
            event.x + 30,
            event.y + 20,
            fill="lightblue",
            tags=("node", node_tag)
        )

        canvas.create_text(
            event.x,
            event.y,
            text="Switch",
            tags=("node", node_tag)
        )

    elif selected_tool == "router":
        canvas.create_rectangle(
            event.x - 30,
            event.y - 20,
            event.x + 30,
            event.y + 20,
            fill="lightblue",
            tags=("node", node_tag)
        )

        canvas.create_text(
            event.x,
            event.y,
            text="Router",
            tags=("node", node_tag)
        )

    selected_tool = None

canvas.bind("<Button-1>", canvas_clicked)
canvas.tag_bind("node", "<Button-1>", node_clicked)

def select_tool(tool):
    global selected_tool
    selected_tool = tool
    print(tool, " placement mode")

host_button = tk.Button(
    sidebar, 
    text="Host",
    command=lambda: select_tool("host")
)
switch_button = tk.Button(
    sidebar, 
    text="Switch",
    command=lambda: select_tool("switch")
)

router_button = tk.Button(
    sidebar, 
    text="Router",
    command=lambda: select_tool("router")
)

host_button.pack(fill="x", padx=10, pady=10)
switch_button.pack(fill="x", padx=10, pady=10)
router_button.pack(fill="x", padx=10, pady=10)


root.mainloop()