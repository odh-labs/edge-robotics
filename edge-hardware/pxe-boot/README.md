The context is a realistic factory setting for operations edge use cases:
- Operational Technology team runs it
- No Internet access / images, logics, buildfile (eg ks) need to be on a single server
- No major resource constraints (think SNO, or OCP, no need for MicroShift)
- Pug-in NUC to boot and image itself with RHEL 8.7 with Podman and MicroShift (rpm) installed.

The PXE Boot automation should:
- Create a PXE server environment
- Automatically install RHEL Device Edge on the target NUC representing the Edge device.
