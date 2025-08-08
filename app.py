import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

import os
from pathlib import Path

from datetime import datetime


# Create a directory to store uploads (once per app run)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def save_file(file, name):
    if file:
        extension = file.name.split('.')[-1]
        filepath = UPLOAD_DIR / f"{email.replace('@', '_at_')}_{name}.{extension}"
        with open(filepath, "wb") as f:
            f.write(file.getvalue())
        return str(filepath)
    return ""

st.title("📈 HPC Assignment 2: Scaling Benchmark Submission")

st.markdown("""
The purpose of this problem is to demonstrate the scaling behaviour of the stencil_mpi program’s
domain decomposition approach to parallelising the solution to Laplace’s equation.
In this worksheet you will run the stencil_mpi program on the Lengau cluster using 2 to 48
processors, as given in the table below, and report the time to complete each run. You should use
values for n and niters that are large enough to show the effects of timing.
Make sure that n is divisible by the various choices of px and py.
Note that n and niters must be the same for all runs — by fixing the problem size you are testing
strong scaling.
""")

# --- SECTION A: Email and parameters ---
st.header("1. Student Info and Fixed Parameters")
email = st.text_input("Enter your email address:", placeholder="you@example.com")
n      = st.number_input("Value of n:", min_value=1, step=1000, value=48000, key="n_key")
niters = st.number_input("Number of iterations (niters):", min_value=1, step=10, value=100, key="niters_key")

# --- SECTION B: Benchmark Table ---
st.header("2. Enter Your Benchmark Results")

st.markdown("Enter the time and speed-up for each configuration you completed. Leave the others blank.")

data = [
    {"p": 2, "px × py": "1×2", "Time (s)": None, "Speed-up": None},
    {"p": 4, "px × py": "1×4", "Time (s)": None, "Speed-up": None},
    {"p": 4, "px × py": "2×2", "Time (s)": None, "Speed-up": None},
    {"p": 6, "px × py": "1×6", "Time (s)": None, "Speed-up": None},
    {"p": 6, "px × py": "2×3", "Time (s)": None, "Speed-up": None},
    {"p": 8, "px × py": "2×4", "Time (s)": None, "Speed-up": None},
    {"p": 9, "px × py": "3×3", "Time (s)": None, "Speed-up": None},
    {"p": 12, "px × py": "3×4", "Time (s)": None, "Speed-up": None},
    {"p": 16, "px × py": "4×4", "Time (s)": None, "Speed-up": None},
    {"p": 18, "px × py": "3×6", "Time (s)": None, "Speed-up": None},
    {"p": 24, "px × py": "4×6", "Time (s)": None, "Speed-up": None},
    {"p": 32, "px × py": "4×8", "Time (s)": None, "Speed-up": None},
    {"p": 36, "px × py": "6×6", "Time (s)": None, "Speed-up": None},
    {"p": 48, "px × py": "6×8", "Time (s)": None, "Speed-up": None},
]

editable_df = pd.DataFrame(data)
updated_df = st.data_editor(
    editable_df,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "p": st.column_config.NumberColumn("p", disabled=True),
        "px × py": st.column_config.TextColumn("px × py", disabled=True),
        "Time (s)": st.column_config.NumberColumn("Time (s)", step=0.1),
        "Speed-up": st.column_config.NumberColumn("Speed-up", step=0.1),
    },
    key="benchmark_table"
)

st.markdown("""After listing the parameters you used for n and niters, fill in the run time in the above table for the
values of px and py used for each run""")




# --- SECTION C: Observations ---
st.header("3. Observations")


st.markdown("""Note that you do not need to do all of the above combinations, but try complete at least eight (8) of
them, with at least three of your runs using 2 nodes,
You could use a different PBS job script file for each run. Name them appropriately. (For example,
stencil1x1.pbs, stencil2x2.pbs, stencil2x3.pbs, etc.) And name the output log files using
the same pattern (eg stencil2x3.log, etc.). Or you could use the approach described in the
“Scaling in Practice” section in the Scaling article on Moodle.
Write all your observations and comments in the text block below""")

q1 = st.radio("What type of speed-up did you observe?", ["Linear", "Sub-linear", "Super-linear"])
q1_expl = st.text_area("Explain your answer:")

q2 = st.text_area("Why do run times differ for different px × py combinations for the same p?")
q3 = st.text_area("How does run time T vary with p? What trend did you observe?")

# --- SECTION C: File Uploads ---
st.header("4. Upload Plots")
plot_time_vs_p = st.file_uploader("Upload T vs p plot (PNG, PDF, SVG)", type=["png", "pdf", "svg"])
plot_speedup_vs_p = st.file_uploader("Upload S vs p plot (PNG, PDF, SVG)", type=["png", "pdf", "svg"])


time_plot_path = save_file(plot_time_vs_p, "time_vs_p")
speedup_plot_path = save_file(plot_speedup_vs_p, "speedup_vs_p")

st.header("Building Software")

st.markdown("""
First copy the assignment files from the student00 account into your Lustre sub-directory:
            
```
cd /mnt/lustre/users/$USER
cp -rv ~/../student00/scaling .
cd scaling
```
            """)

st.markdown("""
Then clear the environment and load the MPI compiler and library module

```
module purge
module load chpc/mpich/3.0.4/gcc/6.1.0
```
Note that you will need to include this in the PBSPro job script as well.
Now compile the stencil_mpi program:

```
mpicc -o stencil_mpi -lm printarr_par.cpp stencil_mpi.cpp
```
            
This only needs to be done once to create the executable. Then it’s available for use by your job
scripts.
""")

st.header("Job Script")

st.markdown(""" 
Create a new PBSPro job script that can access up to 2 nodes and 48 MPI processes. See the
Advanced Scripting and Scaling articles on Moodle for details and examples. Feel free to copy the
python3.pbs example job script and modify it for this assignment.
In your job script you will need to run the program with the correct parameters, for example:

```
time mpirun -n 48 -iface ib0 stencil_mpi 48000 1 100 8 6
```

where the 48 MPI processes are distributed in a 8×6 grid. Of course, your PBSPro job script also
needs to request them with

```
#PBS -l select=2:ncpus=24:mpiprocs=24
#PBS -q normal
```
            
for runs from 25 to 48 cores.

For 1 to 24 nodes use

```
#PBS -l select=1:ncpus=24:mpiprocs=24
#PBS -q smp
```

and then the command is something like

```
time mpirun -n 24 stencil_mpi 48000 1 100 4 6
```

Note that the parameters 48000 1 100 remain the same because you are using the same problem
size for all runs. The parameters highlighted are those that specify the number of processors to be
used by stencil_mpi and hence those you will be changing to test scaling.

            """)


# --- SUBMISSION ---
st.header("6. Submit")

if st.button("📤 Submit Results"):
    if not email:
        st.error("Please enter your email address.")
    else:
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Sanitize filename (replace @ and . in email)
        safe_email = email.replace("@", "_at_").replace(".", "_")

        # File name based on email
        filename = f"{safe_email}_results.csv"        
        meta_lines = [
            f"email,{email}",
            f"submission_time,{timestamp}",
            f"n,{n}",
            f"niters,{niters}",
            f"q1,{q1}",
            f"q1_expl,{q1_expl.replace(',', ';')}",
            f"q2,{q2.replace(',', ';')}",
            f"q3,{q3.replace(',', ';')}",
            f"time_vs_p_plot_path,{time_plot_path}",
            f"speedup_vs_p_plot_path,{speedup_plot_path}",
            "",  # Spacer
            updated_df.to_csv(index=False)
        ]
        full_csv = "\n".join(meta_lines)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_csv)
        st.switch_page("pages/home.py")   # <-- home
