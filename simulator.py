import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib
import subprocess

matplotlib.rcParams.update({"font.size":16,"mathtext.fontset":"cm"})

l0 = 1  # Spring equilibrium length (m)
k = 50 # Spring constant (N/m)
m = 2  # Mass of weight (kg)
g = 9.81  # Constant of gravitational acceleration (m/s/s)

s0 = [ # Starting conditions state vector
    3*np.pi/4, # Theta (rad)
    0, # Theta dot (rad/second)
    l0, # l (metres)
    0, # l dot (metres/second)
]  


def derivatives(t, s):
    """Calculate first derivatives of all variables in state vector s"""
    theta, thetadot, l, ldot = s

    thetadotdot = (-g * np.sin(theta) - 2 * thetadot * ldot) / l  # Using second deriv equation derived from Lagrange-Euler
    # For our purposes, don't use x. xdot = ldot anyway so this substitution is fine

    ldotdot = (l * thetadot**2 - (k * (l - l0)) / m + g * np.cos(theta))  # Just replacing x with l-l0 here
    return thetadot, thetadotdot, ldot, ldotdot


tmax = 10  # Maximum time / length of simulation (s)
dt = 0.01  # Time spacing between values calculated (s)

t = np.arange(0, tmax+dt, dt)  # All time values to be used

s = solve_ivp(derivatives,(0,tmax+dt),s0,t_eval=t) # Calculate the state at each time with numerical integration
print(s["message"])
assert s["success"] == True

theta,thetadot,l,ldot = s["y"] # Unpacking the solved angle and length for all t

# Finding the cartesian coordinates of the end of our pendulum
x = l * np.sin(theta)
y = -l * np.cos(theta)

fps = 20
di = int(1/fps/dt)

def animate_frame(i,ax):
    ax.text(0,1,f"Time {i//di/fps}\n$\\theta={round(np.rad2deg(theta[i]),2)}^\\circ$\n"+r"$\dot{\theta}"+f"={round(np.rad2deg(thetadot[i]),2)}^\\circ/s$\n$l={round(l[i],2)}m$\n"+r"$\dot{l}"+f"={round(ldot[i],2)}m/s$",horizontalalignment="left",verticalalignment="center",transform=ax.transAxes)
    trail(i,ax)
    ax.add_patch(Circle((0,0),0.025,zorder=10)) # Anchor of pendulum
    ax.add_patch(Circle((x[i],y[i]),0.05,zorder=10)) # Pendulum mass
    ax.plot((0,x[i]),(0,y[i])) # Draw line connecting the two
    ax.set_xlim(-np.max(l)-0.5,np.max(l)+0.5)
    ax.set_ylim(-np.max(l)-0.5,np.max(l)+0.5) # Make our axes square
    ax.set_aspect("equal",adjustable="box")
    plt.axis("off")
    plt.savefig("frames/{:04d}".format(int(i//di)),dpi=128)
    plt.cla()

def trail(i,ax):
    ax.plot(x[:i],y[:i],c="red")
    # Uncomment below for fading trail

    # ns = 20
    # for j in range(ns):
    #     imin = i-(ns-j)*10
    #     if imin<0:
    #         continue
    #     imax = imin + 1+10
    #     ax.plot(x[imin:imax],y[imin:imax],color="red")

def animate():  
    fig = plt.figure(figsize=(6.25,6.25), dpi=128)
    ax = fig.add_subplot(111)
    for i in range(0,t.size,di):
        print (f"{i//di}/{t.size//di}")
        animate_frame(i,ax)
    render()

def render():
    out = "out.gif" # change to gif or webp
    print("Converting output to",out.split(".")[-1])
    if out.endswith("gif"):
        # subprocess.run(["convert","-loop","0","-delay",str(int(100/fps)),"frames/*.png",out]) # Imagemagick

        # If using ffmpeg (quicker than imagemagick) we need to generate a pallet for the gif
        # Otherwise webp or mp4 is better for sure
        subprocess.run(["ffmpeg","-i","frames/%04d.png","-vf","palettegen","palette.png","-y"])
        subprocess.run(["ffmpeg","-thread_queue_size","1024","-framerate",str(fps),"-i","frames/%04d.png","-i","palette.png","-lavfi","paletteuse",out,"-y"])
    else:    
        subprocess.run(["ffmpeg","-framerate",str(fps),"-i",r"frames/%04d.png","-loop","0","-y",out])
    print("Done",out)

def plot_ltheta(ax: plt.Axes):
    ax.set_title(r"$\theta$ and x vs $t$")
    ax.plot(t,theta)
    ax.plot(t,l-l0)
    ax.set_xlabel("Time (seconds)")
    ax.legend([r"$\theta$",r"x"])

def plot_path(ax: plt.Axes):
    ax.set_title("Path taken by pendulum")
    ax.set_xlabel(r"$x$ (metres)")
    ax.set_ylabel(r"$y$ (metres)")
    ax.plot(x,y)

def plot_info():
    fig = plt.figure(figsize=(13,6.25),dpi=76)
    fig.text(0.01,0.5,f"$k={k}N/m$\n$m={m}kg$\n$g={g}m/s^2$\n$l_0={l0}m$\n$\\theta_0={round(s0[0],2)}rad$")
    ax = fig.subplots(nrows=1,ncols=2)
    plot_ltheta(ax[0])
    plot_path(ax[1])
    fig.savefig("out.png",dpi=128)
    plt.show()

if __name__ == "__main__":
    # plot_info()
    animate()
