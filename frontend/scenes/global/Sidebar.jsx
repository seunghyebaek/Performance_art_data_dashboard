//scenes/global/sidebar.jsx
"use client";

import { useState } from "react";
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  TextField,
  InputAdornment,
  Divider
} from "@mui/material";
import Link from "next/link";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import SearchIcon from "@mui/icons-material/Search";
import PeopleOutlinedIcon from "@mui/icons-material/PeopleOutlined";
import UploadFileOutlinedIcon from "@mui/icons-material/UploadFileOutlined";
import MenuOutlinedIcon from "@mui/icons-material/MenuOutlined";

const Sidebar = () => {
  const [selected, setSelected] = useState("Dashboard");
  const [isOpen, setIsOpen] = useState(true);

  const menuItems = [
    { title: "Dashboard", to: "/", icon: <HomeOutlinedIcon /> },
    { title: "Upload Data", to: "/invoices", icon: <UploadFileOutlinedIcon /> },
    { title: "Manage Project", to: "/projects", icon: <PeopleOutlinedIcon /> },
  ];

  const toggleDrawer = () => setIsOpen(!isOpen);

  return (
    <>
      {!isOpen && (
        <IconButton
          onClick={toggleDrawer}
          sx={{ position: "fixed", top: 16, left: 16, zIndex: 1300 }}
        >
          <MenuOutlinedIcon />
        </IconButton>
      )}

      <Drawer variant="persistent" anchor="left" open={isOpen}>
        <Box sx={{ width: 250 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" p={2}>
            <Typography variant="h6">Decision Mate</Typography>
            <IconButton onClick={toggleDrawer}>
              <MenuOutlinedIcon />
            </IconButton>
          </Box>

          <Box px={2} pb={2}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          <Divider />

          <List>
            {menuItems.map((item) => (
              <ListItem disablePadding key={item.title}>
                <ListItemButton
                  component={Link}
                  href={item.to}
                  selected={selected === item.title}
                  onClick={() => setSelected(item.title)}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.title} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
    </>
  );
};

export default Sidebar;