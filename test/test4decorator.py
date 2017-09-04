def another_function(func):
    """
    A function that accepts another function
    """

    def other_func():
        val = "The result of %s is %s" % (func(),
                                          eval(func())
                                          )
        return val
    return other_func

def a_function():
    """A pretty useless function"""
    return "1+1"

if __name__ == "__main__":
    value = a_function()
    print(value)
    decorator = another_function(a_function)
    print(decorator)
    print(decorator())


import Tkinter as tk

class App:
    """"""

    def __init__(self, parent):
        """Constructor"""
        frame = tk.Frame(parent)
        frame.pack()

        btn22 = tk.Button(frame, text="22", command=lambda: self.printNum(22))
        btn22.pack(side=tk.LEFT)
        btn44 = tk.Button(frame, text="44", command=lambda: self.printNum(44))
        btn44.pack(side=tk.LEFT)

        quitBtn = tk.Button(frame, text="QUIT", fg="red", command=frame.quit)
        quitBtn.pack(side=tk.LEFT)


    def printNum(self, num):
        """"""
        print("You pressed the %s button" % num)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()