-- The initial ARM64 client window clips its QR/login controls at Portal scale.
-- Apply only to the sign-in dialog; leave other Steam windows to Omarchy.
o.window({ class = "^steam$", title = "^Sign in to Steam$" }, {
  float = true,
  center = true,
  size = { 900, 560 },
})
